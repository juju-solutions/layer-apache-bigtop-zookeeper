## Overview
Apache ZooKeeper is a high-performance coordination service for distributed
applications. It exposes common services such as naming, configuration
management, synchronization, and group services in a simple interface so you
don't have to write them from scratch. You can use it off-the-shelf to
implement consensus, group management, leader election, and presence protocols.

## Usage
Deploy a Zookeeper unit. With only one unit, the service will be running in
`standalone` mode:

    juju deploy apache-bigtop-zookeeper zookeeper


## Scaling
Running ZooKeeper in `standalone` mode is convenient for evaluation, some
development, and testing. But in production, you should run ZooKeeper in
`replicated` mode. A replicated group of servers in the same application is
called a quorum, and in `replicated` mode, all servers in the quorum have
copies of the same configuration file.

Scaling Zookeeper to create a quorum is trivial. The following will add two
additional Zookeeper units and will automatically configure them with knowledge
of the other quorum members based on their peer relation to one another:

    juju add-unit -n 2 apache-bigtop-zookeeper


## Test the deployment
Test if the Zookeeper service is running by using the `zkServer.sh` script:

    juju run --service=apache-bigtop-zookeeper '/usr/lib/zookeeper/bin/zkServer.sh status'

If this command hangs, you can ssh in and run the command on the machine:

    juju ssh apache-bigtop-zookeeper/0
    /usr/lib/zookeeper/bin/zkServer.sh status

TODO: figure out reason for hang.

A successful deployment will report the service mode as either `standalone`
(if only one Zookeeper unit has been deployed) or `leader` / `follower` (if
a Zookeeper quorum has been formed).


## Integrate Zookeeper into another charm
1) Add following lines to your charm's metadata.yaml:

    requires:
      apache-bigtop-zookeeper:
         interface: zookeeper

2) Add a `zookeeper-relation-changed` hook to your charm. Example contents:

    from charmhelpers.core.hookenv import relation_get
    ZK_hostname = relation_get('private-address')
    ZK_port = relation_get('port')



## Contact Information
[bigdata@lists.ubuntu.com](mailto:bigdata@lists.ubuntu.com)


## Help
- [Apache Zookeeper home page](https://zookeeper.apache.org/)
- [Apache Zookeeper issue tracker](https://issues.apache.org/jira/browse/ZOOKEEPER)
- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
