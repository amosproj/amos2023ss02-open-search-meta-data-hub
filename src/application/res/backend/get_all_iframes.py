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
    visualizations = response_data.get('saved_objects', [])

    iframe_codes = []
    for obj in visualizations:
        if obj.get('id') and obj.get('type') == 'visualization':

            # Extract visualization ID
            visualization_id = obj['id']
            encoded_id = urllib.parse.quote(visualization_id)

            # Generate the iframe code
            iframe_code = f'<iframe src="http://localhost:5601/app/visualize#/edit/{encoded_id}?embed=true&_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!t%2Cvalue%3A0)%2Ctime%3A(from%3Anow-15m%2Cto%3Anow))" height="600" width="800"></iframe>'
            iframe_codes.append(iframe_code)

    return iframe_codes
