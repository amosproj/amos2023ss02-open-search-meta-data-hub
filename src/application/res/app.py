import json
from flask import Flask
from flask import render_template
from flask import request
from backend.opensearch_api import OpenSearchManager
from backend import files_type
from backend import get_all_iframes
import urllib

app = Flask(__name__)
index_name = 'amoscore'
os_manager: OpenSearchManager = OpenSearchManager()

"""Rendering start page of the website"""


@app.route('/')
def index():
    return render_template('index.html')


"""rendering page to search in OS"""


@app.route('/search')
def search():
    # response = search_os.simple_search(client = client, search_text = searchField)
    return render_template('search.html')


@app.route('/search/simple')
def search_simple():
    return os_manager.simple_search(index_name, request.args.get('searchString'))


@app.route('/search/advanced')
def search_advanced():
    search_info = json.loads(urllib.parse.unquote(request.args.get('searchString')))
    return os_manager.advanced_search(index_name, search_info)


@app.route('/files_type_chart')
def files_type_chart():
    labels, values, colors = files_type.get_files_type()
    return render_template('doughnut_chart.html', max=17000, set=zip(values, labels, colors))


@app.route('/visualizations')
def visualizations():
    iframe_data = get_all_iframes.get_iframes()
    return render_template('visualizations.html', iframe_data=iframe_data)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
