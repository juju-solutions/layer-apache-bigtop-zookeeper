'''
zookeeper.py
'''

from charmhelpers.core import host
from charms import layer
from charms.layer.apache_bigtop_base import Bigtop
from jujubigdata.utils import run_as, DistConfig
from charmhelpers.core.hookenv import open_port, close_port


class Zookeeper(object):

    def __init__(self, dist_config=None):
        self._dist_config = dist_config or DistConfig(
            data=layer.options('apache-bigtop-base'))

    @property
    def dist_config(self):
        return self._dist_config

    @property
    def _roles(self):
        roles = ['zookeeper-server', 'zookeeper-client']
        return roles

    @property
    def _hosts(self):
        hosts = {}
        return hosts

    @property
    def _override(self):
        override = {}
        return override

    def install(self):
        bigtop = Bigtop()
        bigtop.render_site_yaml(self._hosts, self._roles, self._override)
        bigtop.trigger_puppet()

    def start(self):
        host.service_start('zookeeper-server')

    def stop(self):
        host.service_stop('zookeeper-server')

    def open_ports(self):
        for port in self.dist_config.exposed_ports('zookeeper'):
            open_port(port)

    def close_ports(self):
        for port in self.dist_config.exposed_ports('zookeeper'):
            close_port(port)
        
