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
from backend import files_type
import pandas as pd
from backend import get_all_iframes
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
    all_fields = os_manager.get_all_fields(index_name="amoscore")
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
    html_output = df.to_html(index=False, classes="table table-striped", escape=False)
    return html_output


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
        resultTmp = os_manager.simple_search("amoscore", searchValue)
        session['last_form'] = 'simple'
        if len(resultTmp)>0:
            simpleSearchResult=renderResult(resultTmp)
        else:
            simpleSearchResult="No results found."
    
    if advancedSearchForm.validate_on_submit():
        DEFAULT_WEIGHT=3 # for testing
        i=0
        search_info = {}
        for entry in advancedSearchForm.entry.data:
            parameter_name = entry['metadata_tag']
            search_content = entry['value']
            operator = entry['condition']
            weight=entry['weight']
            search_info[parameter_name] = {
                'search_content': search_content,
                'operator': operator,
                #'weight': DEFAULT_WEIGHT-i
                'weight': weight
            }
            i+=0.5
            print(search_info)
        resultTmp = os_manager.advanced_search(index_name="amoscore", search_info=search_info)
        session['last_form'] = 'advanced'
        if len(resultTmp)>0:
            advancedSearchResult=renderResult(resultTmp)
        else:
            advancedSearchResult="No results found."

    return render_template('search.html',simpleSearchForm=simpleSearchForm,simpleSearchResult=simpleSearchResult, advancedSearchForm=advancedSearchForm, advancedSearchResult=advancedSearchResult,last_form=session.get('last_form'))

#@app.route('/search/simple')
#def search_simple():
#    return os_manager.simple_search("amoscore", request.args.get('searchString')) #Hardcoded indexname
#
#@app.route('/search/advanced')
#def search_advanced():
#    search_info = json.loads(urllib.parse.unquote(request.args.get('searchString'))) #ToDo use Flask Forms
#    return os_manager.advanced_search("amoscore", search_info) #Hardcoded indexname

@app.route('/search/advanced_v2')
def advanced_search_v2():
    return render_template('index1.html')

#@app.route('/files_type_chart')
#def files_type_chart():
#    labels, values, colors = files_type.get_files_type()
#    return render_template('doughnut_chart.html', max=17000, set=zip(values, labels, colors))


@app.route('/visualizations')
def visualizations():
    iframe_data = get_all_iframes.get_iframes()
    return render_template('visualizations.html', iframe_data=iframe_data)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000,debug=True)