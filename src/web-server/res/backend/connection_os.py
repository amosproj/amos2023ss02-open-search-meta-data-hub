from opensearchpy import OpenSearch
import time


def connect_to_os():
    """ connect to OpenSearch """
    host = 'opensearch-node'  # container name of the opensearch node docker container
    port = 9200  # port on which the opensearch node runs
    auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

    """ Create the client with SSL/TLS and hostname verification disabled. """
    # Create the client with SSL/TLS enabled, but hostname verification disabled.
    try:
        client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,  # enables gzip compression for request bodies
            http_auth=auth,
            # client_cert = client_cert_path,
            # client_key = client_key_path,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            # ca_certs = ca_certs_path
        )
    except BaseException:
        # connection error; send error message
        print("ERROR unable to connect opensearch instance")
        return False

    return client
