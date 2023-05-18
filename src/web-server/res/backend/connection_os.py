from opensearchpy import OpenSearch
import time



def connect_to_os():

    """ connect to OpenSearch """
    host = 'opensearch-node' # container name of the opensearch node docker container
    port = 9200 # port on which the opensearch node runs
    auth = ('admin', 'admin') # For testing only. Don't store credentials in code.


    """ Create the client with SSL/TLS and hostname verification disabled. """
    client = OpenSearch(
        hosts = [{'host': host, 'port': port}], # host and port to connect with
        http_auth=auth, # credentials
        use_ssl=False, # disable ssl
        verify_certs=False, # disable verification of certificates
        ssl_assert_hostname=False, # disable verification of hostname
        ssl_show_warn=False, # disable ssl warnings
        retry_on_timeout=True # enable the client trying to reconnect after a timeout
        )

    """ wait till node is ready before performing an import """
    print('\nConnection to OpenSearch Node ...')
    for _ in range(100):
        try:
            client.cluster.health(wait_for_status="yellow") # make sure the cluster is available
        except ConnectionError:
            time.sleep(2) # take a short break to give the opensearch node time to be fully set-up
    print('\nSuccessfully connected!')

    return client
