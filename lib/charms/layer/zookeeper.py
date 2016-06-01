'''
zookeeper.py
'''

from charmhelpers.core import host
from charms import layer
from charms.layer.apache_bigtop_base import Bigtop
from jujubigdata.utils import DistConfig
from charmhelpers.core.hookenv import open_port, close_port, log, unit_get

def format_node(unit, node_ip):
    '''
    Transform the node spec that we get from a client into a string
    that can be written out to a config.

    We can drop the "unit" info, as that is charm specific stuff -- we
    just need the IP address.

    '''
    return "{ip}:2888:3888".format(ip=node_ip)

class Zookeeper(object):
    '''
    Utility class for managing Zookeeper tasks like configuration, start,
    stop, incrementing and decrementing quorum.

    '''
    def __init__(self, dist_config=None):
        self._dist_config = dist_config or DistConfig(
            data=layer.options('apache-bigtop-base'))

        self._roles = ['zookeeper-server', 'zookeeper-client']
        self._hosts = {}
        self._peers = []

    def _read_peers(self):
        self._peers = []  # Reset -- the state in our charm is
                          # secondary to the state on the actual
                          # server.
        # TODO: Get rid of hard coded path below.
        # (Need to figure out how to read the config back out of BigTop.)
        with open("/usr/lib/zookeeper/conf/zoo.cfg", "r") as zoo_cfg:
            for line in zoo_cfg.readlines():
                if line.startswith("server."):
                    self._peers.append(line.strip().split("=")[1])

    @property
    def dist_config(self):
        '''
        Charm level config.

        '''
        return self._dist_config

    def peers(self):
        '''
        List of Zookeeper nodes that we have running.

        '''
        return self._peers

    @property
    def _override(self, peers=None):
        override = {
            "bigtop::hadoop_head_node": unit_get('private-address'),
        }
        if self._peers:
            override["hadoop_zookeeper::server::ensemble"] = self._peers

        return override

    def install(self):
        '''
        Write out the config, then run puppet.

        After this runs, we should have a configured and running service.
        '''
        bigtop = Bigtop()
        log("Rendering site yaml with overrides: {}".format(self._override))
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
        self._read_peers()
        log("Increasing quorum with node_list: {}".format(node_list))
        nodes = [format_node(*node) for node in node_list]
        for node in nodes:
            if not node in self._peers:
                self._peers.append(node)

        self.install()   # update config and trigger puppet

    def decrease_quorum(self, node_list):
        '''
        Remove nodes.

        Will trigger a config update and restart.

        '''
        self._read_peers()
        nodes = [format_node(*node) for node in node_list]
        self._peers = [peer for peer in self._peers if peer not in nodes]

        self.install()  # update config and trigger puppet
