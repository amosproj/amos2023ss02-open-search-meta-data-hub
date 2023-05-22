from flask import Flask
from flask import render_template
from flask import request
from opensearchpy import OpenSearch

from backend import connection_os
from backend import search_os

app = Flask(__name__)
# TODO: find a better solution
client: OpenSearch = connection_os.connect_to_os()

labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


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


@app.route('/pie')
def pie():
    pie_labels = labels
    pie_values = values
    return render_template('pie_chart.html', max=17000, set=zip(values, labels, colors))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
