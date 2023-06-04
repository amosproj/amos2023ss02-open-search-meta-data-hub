import json
from flask import Flask
from flask import render_template
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FieldList, FormField, Form
from wtforms.validators import DataRequired
from backend.opensearch_api import OpenSearchManager
from backend import files_type
import urllib

app = Flask(__name__)
index_name = 'amoscore'
os_manager: OpenSearchManager = OpenSearchManager()


class ItemForm(Form):
    tag = StringField('tag', validators=[DataRequired()])
    searchOperator = SelectField('searchOperator', [('tag_exists', 'tag exists'),('tag_not_exist', 'tag not exists'),('', '────────────────'), ('field_is_empty', 'field is empty'),('field_is_not_empty', 'field is not empty'),('', '────────────────'),('contains', 'contains'),('not_contains', 'not contains'),('', '────────────────'),('is_equal', 'is equal'),('is_not_equal', 'is not equal'),('', '────────────────'),('is_greater', 'is greater'),('is_smaller', 'is smaller')], validators=[DataRequired()])
    searchValue = StringField('searchValue', validators=[DataRequired()])

class advancedSearchForm(FlaskForm):
    items = FieldList(FormField(ItemForm), min_entries=1)

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
    return os_manager.simple_search("amoscore", request.args.get('searchString')) #Hardcoded indexname

@app.route('/search/advanced')
def search_advanced():
    search_info = json.loads(urllib.parse.unquote(request.args.get('searchString'))) #ToDo use Flask Forms
    return os_manager.advanced_search("amoscore", search_info) #Hardcoded indexname

@app.route('/search/advanced_v2')
def advanced_search_v2():
    form = advancedSearchForm()
    if form.validate_on_submit():
        # ... 
        pass
    return render_template('index1.html')

@app.route('/files_type_chart')
def files_type_chart():
    labels, values, colors = files_type.get_files_type()
    return render_template('doughnut_chart.html', max=17000, set=zip(values, labels, colors))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
