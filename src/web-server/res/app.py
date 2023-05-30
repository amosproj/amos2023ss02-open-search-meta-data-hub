from flask import Flask
from flask import render_template
from flask import request
from opensearchpy import OpenSearch
from backend import connection_os
from backend import search_os
from backend import files_type

app = Flask(__name__)
# TODO: find a better solution
client: OpenSearch = connection_os.connect_to_os()


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
    return search_os.simple_search(client, request.args.get('searchString'))

@app.route('/search/advanced')
def search_advanced():
    return search_os.advanced_search(client, request.args.get('searchInfo'))

@app.route('/files_type_chart')
def files_type_chart():
    labels,values,colors=files_type.get_files_type()
    return render_template('doughnut_chart.html', max=17000, set=zip(values, labels, colors))




if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)