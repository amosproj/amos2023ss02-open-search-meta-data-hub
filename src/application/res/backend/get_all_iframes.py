import requests
import urllib.parse
import json
from datetime import datetime
from dateutil import tz

localhost = False


def get_iframes():
    # Fetch visualizations
    url = 'http://localhost:5601/api/saved_objects/_find?type=visualization' if localhost else 'http://opensearch-dashboards:5601/api/saved_objects/_find?type=visualization'
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
            updated_at_human_readable = convert_time(obj['updated_at'])

            # Generate the iframe code
            iframe_code = f'<iframe src="http://localhost:5601/app/visualize#/edit/{encoded_id}?embed=true&_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!t%2Cvalue%3A0)%2Ctime%3A(from%3Anow-15m%2Cto%3Anow))" height="600" width="800"></iframe>'

            # Add the data to the iframe_data list
            iframe_data.append({
                'title': title,
                'type': vis_type,
                'updated_at': updated_at_human_readable,
                'iframe_code': iframe_code
            })

    return iframe_data


def convert_time(updated_at_ts):
    utc_dt = datetime.fromisoformat(updated_at_ts[:-1]).replace(tzinfo=tz.tzutc())
    german_tz = tz.gettz('Europe/Berlin')
    german_dt = utc_dt.astimezone(german_tz)
    updated_at_human_readable = german_dt.strftime('%b %d, %Y - %H:%M:%S')
    return updated_at_human_readable
