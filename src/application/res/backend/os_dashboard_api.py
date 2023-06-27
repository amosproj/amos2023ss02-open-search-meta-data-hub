import requests
import urllib.parse
import json
from datetime import datetime
from dateutil import tz


def _convert_time(updated_at_ts):
    utc_dt = datetime.fromisoformat(updated_at_ts[:-1]).replace(tzinfo=tz.tzutc())
    german_tz = tz.gettz('Europe/Berlin')
    german_dt = utc_dt.astimezone(german_tz)
    updated_at_human_readable = german_dt.strftime('%b %d, %Y - %H:%M:%S')
    return updated_at_human_readable


class OSDashboardManager:
    """
     Class for managing the connection to the OpenSearch-Dashboard detects new visualizations.
     class is a basic skeleton, and you may need to add more methods and functionality based
     on your specific requirements.
     """

    def __init__(self, localhost: bool = False):
        """
        Create a new OSDashboardManager for handling the connection to OpenSearch-Dashboard.

        :param localhost: A boolean variable that defines whether to connect to a local instance or
                          the docker container.
                          If not set to True, it will automatically connect to the docker container.
        """

        self._set_host(localhost)  # set the host for the OpenSearch connection

    def _set_host(self, localhost: bool):
        """ Setting the host for the OpenSearchDashboard connection
        :param localhost: A bool variable that defines whether
        to connect to a local instance or the docker container
        """
        if localhost:
            self._host = 'localhost'  # connection to localhost (testing purposes)
        else:
            self._host = 'opensearch-dashboards'  # connection to docker container
        self._port = 5601

    def get_iframes(self):
        """
        Fetches visualizations from the OpenSearch-Dashboard and extracts the relevant information
        :return: a list of dictionaries which contain the title, the type, the date of the last update and the
        iframe_code of all saved visualization of the OpenSearch-Dashboard
        """
        # Fetch visualizations
        url = f'http://{self._host}:{self._port}/api/saved_objects/_find?type=visualization'
        headers = {
            'Content-Type': 'application/json',
            'kbn-xsrf': 'true'  # Add this header if required by your OpenSearch Dashboards instance
        }

        response = requests.get(url, headers=headers)
        response_data = response.json()
        visualizations = response_data.get('saved_objects', [])
        iframe_data = []
        for obj in visualizations:
            if obj.get('id') and obj.get('type') == 'visualization':
                # Extract visualization information
                visualization_id = obj['id']
                encoded_id = urllib.parse.quote(visualization_id)
                title = obj['attributes']['title'].capitalize()
                vis_state = json.loads(obj['attributes']['visState'])
                vis_type = vis_state['type'].capitalize()

                # get and convert last update time
                updated_at_human_readable = _convert_time(obj['updated_at'])

                # Generate the iframe code
                iframe_code = f'http://localhost:5601/app/visualize#/edit/{encoded_id}?embed=true&_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!t%2Cvalue%3A0)%2Ctime%3A(from%3Anow-15m%2Cto%3Anow))'

                # Add the data to the iframe_data list
                iframe_data.append({
                    'title': title,
                    'type': vis_type,
                    'updated_at': updated_at_human_readable,
                    'iframe_code': iframe_code
                })

        return iframe_data
