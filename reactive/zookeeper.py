'''
Reactive handlers for Zookeeper.
'''

from charmhelpers.core import hookenv
from charms.layer.zookeeper import Zookeeper
from charms.reactive import set_state, when, when_not

@when('bigtop.available')
@when_not('zookeeper.installed')
def install_zookeeper(*args):
    '''
    After Bigtop has done the initial setup, trigger a puppet install,
    via our Zooekeeper library.

    '''
    zk = Zookeeper()
    zk.install()
    zk.open_ports()
    set_state('zookeeper.installed')
    set_state('zookeeper.started')    
    hookenv.status_set('active', 'Ready')    

@when('zookeeper.started')
def restart_zookeeper_if_config_changed():
    pass

@when('zookeeper.started', 'config.changed.rest')
def rest_config():
    pass

@when('zookeeper.started', 'zkpeer.joined')
def quorum_add(zkpeer):
    pass

@when('zookeeper.started', 'zkpeer.departed')
def quorum_remove(zkpeer):
    pass

@when('zookeeper.started', 'zkclient.joined')
def serve_client(client):
    pass
