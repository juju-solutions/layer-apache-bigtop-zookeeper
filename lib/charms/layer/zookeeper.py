'''
zookeeper.py
'''

from charmhelpers.core import host
from charms import layer
from charms.layer.apache_bigtop_base import Bigtop
from jujubigdata.utils import DistConfig
from charmhelpers.core.hookenv import open_port, close_port


def getid(unit_id):
    """Utility function to return the unit number."""
    return unit_id.split("/")[1]


class Zookeeper(object):
    '''
    Utility class for managing Zookeeper tasks like configuration, start,
    stop, incrementing and decrementing quorum.

    '''
    def __init__(self, dist_config=None):
        self._dist_config = dist_config or DistConfig(
            data=layer.options('apache-bigtop-base'))

        self._peers = []

    @property
    def dist_config(self):
        '''
        Charm level config.

        '''
        return self._dist_config

    @property
    def _roles(self):
        '''
        List of specific services that we want to deploy. Will be passed
        to Bigtop.

        '''
        return ['zookeeper-server', 'zookeeper-client']

    @property
    def _hosts(self):
        '''
        Dict of hosts to pass to Bigtop.

        # TODO: do we actually need to populate this? If so, we need
        to popualte it.

        '''
        hosts = {}
        return hosts

    @property
    def peers(self):
        '''
        List of Zookeeper nodes that we theoretically have running.

        # TODO: probably safer to read these out of the config each
        # time, so that we aren't keeping extra state around.

        '''
        return self._peers

    @property
    def _override(self):
        '''
        Dict of parameters used to override the puppet config.

        '''
        return {
            "hadoop_zookeeper::server::ensemble": self.peers,
            # @HACK: need to remove override, or override with
            # something correct.
            "bigtop::hadoop_head_node": "foo.qux:2888:3888"
        }

    def install(self):
        '''
        Write out the config, then run puppet.

        After this runs, we should have a configured and running service.
        '''
        bigtop = Bigtop()
        bigtop.render_site_yaml(self._hosts, self._roles, self._override)
        bigtop.trigger_puppet()

    def start(self):
        '''
        Request that our service start. Normally, puppet will handle this
        for us.

        '''
        host.service_start('zookeeper-server')

    def stop(self):
        '''
        Stop Zookeeper.

        '''
        host.service_stop('zookeeper-server')

    def open_ports(self):
        '''
        Expose the ports in the configuration to the outside world.

        '''
        for port in self.dist_config.exposed_ports('zookeeper'):
            open_port(port)

    def close_ports(self):
        '''
        Close off communication from the outside world.

        '''
        for port in self.dist_config.exposed_ports('zookeeper'):
            close_port(port)

    def increase_quorum(self, node_list):
        '''
        Add a nodes.

        Will trigger a config update and restart.

        '''
        for unit_id, unit_ip in node_list:
            entry = "server.{}={}:2888:3888".format(getid(unit_id), unit_ip)
            if entry not in self._peers:
                # TODO: Flatten nested loop.
                self._peers.append(entry)
        self.install()   # update config and trigger puppet

    def decrease_quorum(self, node_list):
        '''
        Remove nodes.

        Will trigger a config update and restart.

        '''
        for unit_id, unit_ip in node_list:
            entry = "server.{}={}:2888:3888".format(getid(unit_id), unit_ip)
            # TODO: flatten these nested loops
            self._peers = [peer for peer in self._peers if peer != entry]

        self.install()  # update config and trigger puppet
