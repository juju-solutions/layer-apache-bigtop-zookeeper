'''
zookeeper.py
'''

from charmhelpers.core import host
from charms import layer
from charms.layer.apache_bigtop_base import Bigtop
from jujubigdata.utils import DistConfig
from charmhelpers.core.hookenv import open_port, close_port


def format_node(node_id, node_ip):
    '''
    Transform the node spec that we get from a client into a string
    that can be written out to a config.

    '''
    return "server.{}={}:2888:3888".format(node_id.split("/")[1], node_ip)

class Zookeeper(object):
    '''
    Utility class for managing Zookeeper tasks like configuration, start,
    stop, incrementing and decrementing quorum.

    '''
    def __init__(self, dist_config=None):
        self._dist_config = dist_config or DistConfig(
            data=layer.options('apache-bigtop-base'))

        self._peers = []
        self._roles = ['zookeeper-server', 'zookeeper-client']
        self._hosts = {}
        self._override = {
            "hadoop_zookeeper::server::ensemble": self.peers,
            # @HACK: need to remove override, or override with
            # something correct.
            "bigtop::hadoop_head_node": "foo.qux:2888:3888"
        }

    @property
    def dist_config(self):
        '''
        Charm level config.

        '''
        return self._dist_config

    @property
    def peers(self):
        '''
        List of Zookeeper nodes that we have running.

        # TODO: probably safer to read these out of the config each
        # time, so that we aren't keeping extra state around.

        '''
        return self._peers

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
        nodes = [format_node(*node) for node in node_list]
        self._peers = list(set(nodes + self._peers))  # Combine and dedupe

        self.install()   # update config and trigger puppet

    def decrease_quorum(self, node_list):
        '''
        Remove nodes.

        Will trigger a config update and restart.

        '''
        nodes = [format_node(*node) for node in node_list]
        self._peers = [peer for peer in self._peers if peer not in nodes]

        self.install()  # update config and trigger puppet
