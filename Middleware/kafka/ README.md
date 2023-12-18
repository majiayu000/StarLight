# What is Kafka?

Apache Kafka® is an event streaming platform.

With the release of Apache Kafka 3.5, Zookeeper is now marked deprecated.

So, this project is a simple example of how to use Kafka without Zookeeper.


# Run

```bash
curl -sSL https://raw.githubusercontent.com/bitnami/containers/main/bitnami/kafka/docker-compose.yml > docker-compose.yml
docker-compose up -d
```

# Key Features

- Low latency: up to 10 milliseconds latency, for large volumes of data.
- High Scalability
- High Fault Tolerance: Kafka is very fault-tolerant and reliable since it duplicates and distributes your data often to other servers or Brokers
- Multiple Integrations: Kafka can interface with a variety of Data-Processing Frameworks and Services, including Apache Spark, Apache Storm, Hadoop, and Amazon Web Services. 

# Kafka Cluster Architecture

###  concepts
A kafka client is a cluster.Kafka with more than one broker is called Kafka Cluster. It can be expanded and used without downtime. 

## Topics

A Kafka Topic is a **Collection of Messages** that belong to a given category or feed name.Topics are used to arrange all of Kafka’s records. Consumer apps read data from Topics, whereas Producer applications write data to them. 

In Kafka, Topics are segmented into a customizable number of sections called **Partitions**. Kafka Partitions allow several users to read data from the same subject at the same time.

## Broker

The Kafka Server is known as Broker, which is in charge of the Topic’s **Message Storage**.

Assume there are three broker called A｜B｜C and message is written in topic T whose leader is broker A. When A received message, it will copy the message to B and C. If B is down, A will copy the message to C. When B is up, B will copy the message from C. A is responsible for the client to read and write data. B and C are responsible for backing up data.

## ~~Zookeeper~~ Kraft

Apache Kafka Raft (KRaft) is the consensus protocol that was introduced in KIP-500 to remove Apache Kafka’s dependency on ZooKeeper for metadata management.
KRaft mode is production ready for new clusters as of Apache Kafka 3.3. 

### Difference between Zookeeper and Kraft

May be the biggest difference is that I can use `bootstrap.servers=broker:9092` instead of `zookeeper.connect=zookeeper:2181`.

## Producer

Within the Kafka Clusters, a Producer Sends or Publishes Data/Messages to the Topic. **Producer delivers messages as quickly as the Broker can handle them without acknowledge them**.

When a Producer adds a record to a Topic, it is published to the Topic’s Leader. The record is appended to the Leader’s Commit Log, and the record offset is increased. Each piece of data that comes in will be piled on the cluster, and Kafka only exposes a record to a Consumer when it has been committed.

Hence, it is crucial that Producers must first obtain metadata about the Kafka Clusters from the Broker before sending any records.

## Consumer

The Broker will distribute messages based on which Consumers should read from which Partitions, as well as keeping track of the group’s offset for each Partition. It keeps track of this by requiring all customers to declare which offsets they have handled.



# Get started

## Docker Installation

```bash
curl -sSL https://raw.githubusercontent.com/bitnami/containers/main/bitnami/kafka/docker-compose.yml > docker-compose.yml
docker-compose up -d
```


# Problem and Solution

## Temporary failure in name resolution

This is because the docker network? can not resolve the host name.

Add 0.0.0.0 kafka to /etc/hosts, then use kafka:9092 as bootstrap.servers.

## Consumers consumer same message

If you want to consume the same message in a topic partition, you need to set the ~~same~~different group.id.


