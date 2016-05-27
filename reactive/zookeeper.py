'''
Reactive handlers for Zookeeper.
'''

from charmhelpers.core import hookenv
from charms.layer.zookeeper import Zookeeper
from charms.reactive import set_state, when, when_not

@when('bigtop.available')
@when_not('zookeeper.installed')
def install_zookeeper():
    '''
    After Bigtop has done the initial setup, trigger a puppet install,
    via our Zooekeeper library.

    puppet will start the service, as a side effect.

    '''
    zk = Zookeeper()
    zk.install()
    zk.open_ports()
    set_state('zookeeper.installed')
    set_state('zookeeper.started')
    hookenv.status_set('active', 'Ready')

@when('zookeeper.started', 'config.changed.rest')
def rest_config():
    """TODO"""
    pass

@when('zookeeper.started', 'zkpeer.joined')
def quorum_add(zkpeer):
    """Add a zookeeper peer.

    Add the unit that just joined, restart Zookeeper, and remove the
    '.joined' state so we don't fall in here again (until another peer joins).
    """
    nodes = zkpeer.get_nodes()  # single node since we dismiss .joined below
    zk = Zookeeper()
    zk.increase_quorum(nodes)
    #restart_zookeeper_if_config_changed()  # Not necessary due to puppet
    zkpeer.dismiss_joined()

@when('zookeeper.started', 'zkpeer.departed')
def quorum_remove(zkpeer):
    """Remove a zookeeper peer.

    Remove the unit that just departed, restart Zookeeper, and remove the
    '.departed' state so we don't fall in here again (until another peer leaves).
    """
    nodes = zkpeer.get_nodes()  # single node since we dismiss .departed below
    zk = Zookeeper()
    zk.decrease_quorum(nodes)
    #restart_zookeeper_if_config_changed()  # puppet handles now
    zkpeer.dismiss_departed()

@when('zookeeper.started', 'zkclient.joined')
def serve_client(client):
    """TODO"""
    pass
