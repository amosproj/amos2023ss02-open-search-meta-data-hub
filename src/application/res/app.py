import secrets
import json
from flask import Flask
from flask import render_template
from flask import request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SelectField, FieldList, FormField, Form, SubmitField
from wtforms.validators import DataRequired
from backend.opensearch_api import OpenSearchManager
from backend import files_type
import pandas as pd
import urllib

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

os_manager: OpenSearchManager = OpenSearchManager(localhost=True)

    
class SimpleSearchForm(FlaskForm):
    searchValue = StringField('Search Value', validators=[DataRequired()])
    submit = SubmitField('Search')

class AdvancedEntryForm(FlaskForm):
    metadata_tag = StringField('Metadata tag')
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
    html_output = df.to_html(index=False, classes="table table-striped", escape=False)
    return html_output


"""Rendering start page of the website"""
@app.route('/')
def index():
    return render_template('index.html')


"""rendering page to search in OS"""


@app.route('/search')
def search():
    # response = search_os.simple_search(client = client, search_text = searchField)
    return render_template('search.html')   

@app.route('/simpleSearch', methods=['GET', 'POST'])
def simpleSearch():
    simpleSearchForm = SimpleSearchForm()
    simpleSearchResult = ""
    advancedSearchForm = AdvancedSearchForm()
    advancedSearchResult = ""
    if simpleSearchForm.validate_on_submit():
        searchValue = simpleSearchForm.searchValue.data
        resultTmp = os_manager.simple_search("amoscore", searchValue)
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
            search_info[parameter_name] = {
                'search_content': search_content,
                'operator': operator
            }
            print(search_info)
        resultTmp = os_manager.advanced_search(index_name="amoscore", search_info=search_info)
        if len(resultTmp)>0:
            advancedSearchResult=renderResult(resultTmp)
        else:
            advancedSearchResult="No results found."

    return render_template('simpleSearch.html',simpleSearchForm=simpleSearchForm,simpleSearchResult=simpleSearchResult, advancedSearchForm=advancedSearchForm, advancedSearchResult=advancedSearchResult)

@app.route('/search/simple')
def search_simple():
    return os_manager.simple_search("amoscore", request.args.get('searchString')) #Hardcoded indexname

@app.route('/search/advanced')
def search_advanced():
    search_info = json.loads(urllib.parse.unquote(request.args.get('searchString'))) #ToDo use Flask Forms
    return os_manager.advanced_search("amoscore", search_info) #Hardcoded indexname

@app.route('/search/advanced_v2')
def advanced_search_v2():
    return render_template('index1.html')

@app.route('/files_type_chart')
def files_type_chart():
    labels, values, colors = files_type.get_files_type()
    return render_template('doughnut_chart.html', max=17000, set=zip(values, labels, colors))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
