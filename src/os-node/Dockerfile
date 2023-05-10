FROM opensearchproject/opensearch:latest

# Name the cluster
#ENV cluster.name=opensearch-cluster
# Name the node that will run in this container
#ENV node.name=opensearch-node
# Nodes to look for when discovering the cluster
#ENV discovery.seed_hosts=opensearch-node
# Nodes eligibile to server as cluster manager
#ENV cluster.initial_cluster_manager_nodes=opensearch-node
# Disable JVM heap memory swapping
#ENV bootstrap.memory_lock=true
# Set min and max JVM heap sizes to at least 50% of system RAM
#ENV OPENSEARCH_JAVA_OPTS="-Xms512m -Xmx512m"
# Prevents execution of bundled demo script which installs demo certificates and security configurations to OpenSearch
#ENV DISABLE_INSTALL_DEMO_CONFIG=true
# Disables Security plugin
#ENV DISABLE_SECURITY_PLUGIN=true

RUN mkdir WORK_REPO
#WORKDIR /WORK_REPO
ADD res .
