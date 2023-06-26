import secrets
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SelectField, FieldList, FormField, Form, SubmitField, IntegerField, validators
from wtforms.validators import DataRequired
from backend.opensearch_api import OpenSearchManager
from backend.os_dashboard_api import OSDashboardManager
import pandas as pd
import urllib
from backend.helper_functions import create_config_parser

config=create_config_parser()

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

os_dashboard_manager : OSDashboardManager = OSDashboardManager(localhost=config.get('General','localhost'))
os_manager: OpenSearchManager = OpenSearchManager(localhost=config.get('General','localhost'))

    
class SimpleSearchForm(FlaskForm):
    searchValue = StringField('Search Value', validators=[DataRequired()])
    submit = SubmitField('Search')

class AdvancedEntryForm(FlaskForm):
    all_fields = os_manager.get_all_fields(index_name=config.get('Opensearch_Dashboard','default_index_name'))
    metadata_tag = SelectField('Metadata tag', choices=all_fields)
    condition = SelectField('Condition', choices=[
        ('tag_exists', 'tag exists'), 
        ('tag_not_exist', 'tag not exists'),
        ('field_is_empty', 'field is empty'), 
        ('field_is_not_empty', 'field is not empty'),
        ('contains', 'contains'), 
        ('not_contains', 'not contains'),
        ('is_equal', 'is equal'), 
        ('is_not_equal', 'is not equal'),
        ('is_greater', 'is greater'), 
        ('is_smaller', 'is smaller')])
    value = StringField('Value')
    weight = IntegerField('Weight', [validators.NumberRange(min=1, max=100, message="Weight must be between 1 and 100")],default=1)


class AdvancedSearchForm(FlaskForm):
    entry = FieldList(FormField(AdvancedEntryForm), min_entries=1)
    submit = SubmitField('Submit')

def renderResult(input):
    # Extract the relevant list from the dictionary
    hits_list = input['hits']['hits']
    # Create a DataFrame with only FileName, FileSize, FileInodeChangeDate and a button
    df = pd.DataFrame([{
        'HitCount': idx + 1, 
        'FileName': item['_source']['FileName'], 
        'FileSize': item['_source']['FileSize'], 
        'ChangeDate': item['_source']['FileInodeChangeDate'], 
        'Details': '<button class="btn btn-info" onclick="showDetails(this)" data-hit=\'{}\'>Show Details</button>'.format(json.dumps(item['_source']))
    } for idx, item in enumerate(hits_list)])
    # Convert the DataFrame to HTML and apply Bootstrap classes
    df_html = df.to_html(index=False, classes="table", escape=False)

    return df_html


"""Rendering start page of the website"""
@app.route('/')
def index():
    return render_template('index.html')


"""rendering page to search in OS"""


#@app.route('/search')
#def search():
#    # response = search_os.simple_search(client = client, search_text = searchField)
#    return render_template('search.html')   

@app.route('/search', methods=['GET', 'POST'])
def search():
    session['last_form'] = 'simple'
    simpleSearchForm = SimpleSearchForm()
    simpleSearchResult = ""
    advancedSearchForm = AdvancedSearchForm()
    advancedSearchResult = ""
    if simpleSearchForm.validate_on_submit():
        searchValue = simpleSearchForm.searchValue.data
        resultTmp = os_manager.simple_search(config.get('Opensearch_Dashboard','default_index_name'), searchValue)
        session['last_form'] = 'simple'
        if len(resultTmp)>0:
            simpleSearchResult=renderResult(resultTmp)
        else:
            simpleSearchResult="No results found."
    
    if advancedSearchForm.validate_on_submit():
        search_info = {}
        for entry in advancedSearchForm.entry.data:
            parameter_name = entry['metadata_tag']
            search_content = entry['value']
            operator = entry['condition']
            weight=entry['weight']
            search_info[parameter_name] = {
                'search_content': search_content,
                'operator': operator,
                'weight': weight
            }
            print(search_info)
        resultTmp = os_manager.advanced_search(index_name=config.get('Opensearch_Dashboard','default_index_name'), search_info=search_info)
        session['last_form'] = 'advanced'
        if len(resultTmp)>0:
            advancedSearchResult=renderResult(resultTmp)
        else:
            advancedSearchResult="No results found."

    return render_template('search.html',simpleSearchForm=simpleSearchForm,simpleSearchResult=simpleSearchResult, advancedSearchForm=advancedSearchForm, advancedSearchResult=advancedSearchResult,last_form=session.get('last_form'))

#@app.route('/search/simple')
#def search_simple():
#    return os_manager.simple_search(config.get('Opensearch_Dashboard','default_index_name'), request.args.get('searchString')) #Hardcoded indexname
#
#@app.route('/search/advanced')
#def search_advanced():
#    search_info = json.loads(urllib.parse.unquote(request.args.get('searchString'))) #ToDo use Flask Forms
#    return os_manager.advanced_search(config.get('Opensearch_Dashboard', 'default_index_name'), search_info) #Hardcoded indexname

@app.route('/search/advanced_v2')
def advanced_search_v2():
    return render_template('index1.html')

@app.route('/visualizations')
def visualizations():
    iframe_data = os_dashboard_manager.get_iframes()

    # Pagination settings
    page = int(request.args.get('page', 1))
    per_page = 10  # Number of items per page
    total_items = len(iframe_data)
    total_pages = (total_items + per_page - 1) // per_page  # Calculate total pages

    # Get the current page's data
    start = (page - 1) * per_page
    end = start + per_page
    current_page_data = iframe_data[start:end]

    return render_template('visualizations.html', iframe_data=current_page_data, page=page, total_pages=total_pages)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
