from datetime import time

from opensearchpy import OpenSearch


def connect_to_os() -> OpenSearch:
    """ Connect to OpenSearch """
    host = 'opensearch-node'  # Container name of the OpenSearch node Docker container
    port = 9200  # Port on which the OpenSearch node runs
    auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

    # Create the client with SSL/TLS and hostname verification disabled
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],  # Host and port to connect with
        http_auth=auth,  # Credentials
        use_ssl=False,  # Disable SSL
        verify_certs=False,  # Disable verification of certificates
        ssl_assert_hostname=False,  # Disable verification of hostname
        ssl_show_warn=False,  # Disable SSL warnings
        retry_on_timeout=True  # Enable the client to reconnect after a timeout
    )

    # Wait until the node is ready before performing an import
    for _ in range(100):
        try:
            client.cluster.health(wait_for_status="yellow")  # Make sure the cluster is available
        except ConnectionError:
            time.sleep(2)  # Take a short break to give the OpenSearch node time to be fully set up

    return client
