import requests
import urllib.parse

def get_iframes():
    # Fetch visualizations
    url = 'http://opensearch-dashboards:5601/api/saved_objects/_find?type=visualization'
    headers = {
        'Content-Type': 'application/json',
        'kbn-xsrf': 'true'  # Add this header if required by your OpenSearch Dashboards instance
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    # Extract visualization IDs
    visualization_ids = []
    for obj in response_data.get('saved_objects', []):
        if obj.get('id') and obj.get('type') == 'visualization':
            visualization_ids.append(obj['id'])

    # Generate the iframe code
    iframe_codes = []
    for visualization_id in visualization_ids:
        encoded_id = urllib.parse.quote(visualization_id)
        iframe_code = f'<iframe src="http://localhost:5601/app/visualize#/edit/{encoded_id}?embed=true&_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!t%2Cvalue%3A0)%2Ctime%3A(from%3Anow-15m%2Cto%3Anow))" height="600" width="800"></iframe>'
        iframe_codes.append(iframe_code)

    return iframe_codes
    # Print the iframe codes
    # for iframe_code in iframe_codes:
    #     print(iframe_code)
