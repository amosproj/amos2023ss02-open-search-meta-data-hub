from flask import Flask
from flask import render_template
from opensearchpy import OpenSearch

from backend import connection_os

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
    # response = search_os.simple_search(client = client, search_text = 'image')
    return render_template('search.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
