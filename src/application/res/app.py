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
import configparser

# Configuration Setup
config = configparser.ConfigParser()
config.read('config.ini')

# Flask Application Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Flask Extensions
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

# OSDashboardManager Initialization
os_dashboard_manager: OSDashboardManager = OSDashboardManager(localhost=config.getboolean('General', 'localhost'))

# OpenSearchManager Initialization
os_manager: OpenSearchManager = OpenSearchManager(localhost=config.getboolean('General', 'localhost'),
                                                  search_size=config.getint('General', 'search_size'))


# SimpleSearchForm Definition
class SimpleSearchForm(FlaskForm):
    searchValue = StringField('Search Value', validators=[DataRequired()])
    submit = SubmitField('Search')


class AdvancedEntryForm(FlaskForm):
    # Get all available fields for the specified index
    all_fields = os_manager.get_all_fields(index_name=config.get('General', 'default_index_name'))
    # Dropdown menu for selecting a metadata tag
    metadata_tag = SelectField('Metadata tag', choices=all_fields)
    # Dropdown menu for selecting a condition for the metadata tag
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
    # Text field for entering a value associated with the metadata tag
    value = StringField('Value')
    # Integer field for assigning a weight to the entry
    weight = IntegerField('Weight',
                          [validators.NumberRange(min=1, max=100, message="Weight must be between 1 and 100")],
                          default=1)


# Define a form class for advanced search functionality
class AdvancedSearchForm(FlaskForm):
    """
    Form class for advanced search functionality.

    The form allows users to define multiple search criteria by adding and configuring entries.
    Each entry is represented by an instance of the AdvancedEntryForm form class.
    The form provides fields for specifying metadata tag, condition, value, and weight for the search criteria.
    """
    # Field for defining multiple search criteria entries
    entry = FieldList(FormField(AdvancedEntryForm), min_entries=1)
    # Submit button for submitting the form
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
        'Details': '<button class="btn btn-info" onclick="showDetails(this)" data-hit=\'{}\'>Show Details</button>'.format(
            json.dumps(item['_source']))
    } for idx, item in enumerate(hits_list)])
    # Convert the DataFrame to HTML and apply Bootstrap classes
    df_html = df.to_html(index=False, classes="table", escape=False)

    return df_html


"""Rendering start page of the website"""


@app.route('/')
def index():
    return render_template('index.html')


"""rendering page to search in OS"""


# @app.route('/search')
# def search():
#    # response = search_os.simple_search(client = client, search_text = searchField)
#    return render_template('search.html')   

@app.route('/search', methods=['GET', 'POST'])
def search():
    # Set the last_form session variable to 'simple'
    session['last_form'] = 'simple'

    # Initialize SimpleSearchForm and AdvancedSearchForm
    simpleSearchForm = SimpleSearchForm()
    simpleSearchResult = ""
    advancedSearchForm = AdvancedSearchForm()
    advancedSearchResult = ""

    # Extract field names and data types from 'amoscore' and convert to JSON string
    field_names_data_types = os_manager.extract_metadata_dict('amoscore')
    json_dict = json.dumps(field_names_data_types)

    # Handle simple search form submission
    if simpleSearchForm.validate_on_submit():
        # Get the search value from the form
        searchValue = simpleSearchForm.searchValue.data

        # Perform simple search using the default index name
        resultTmp = os_manager.simple_search(config.get('General', 'default_index_name'), searchValue)

        # Set the last_form session variable to 'simple'
        session['last_form'] = 'simple'

        # Render the search results or display a message if no results found
        if len(resultTmp) > 0:
            simpleSearchResult = renderResult(resultTmp)
        else:
            simpleSearchResult = "No results found."

    # Handle advanced search form submission
    if advancedSearchForm.validate_on_submit():
        # Initialize a dictionary to store search information
        search_info = {}

        # Iterate over each entry in the advanced search form
        for entry in advancedSearchForm.entry.data:
            parameter_name = entry['metadata_tag']
            search_content = entry['value']
            operator = entry['condition']
            weight = entry['weight']

            # Store the search information in the dictionary
            search_info[parameter_name] = {
                'search_content': search_content,
                'operator': operator,
                'weight': weight
            }

        # Perform advanced search using the default index name and the search information
        resultTmp = os_manager.advanced_search(index_name=config.get('General', 'default_index_name'),
                                               search_info=search_info)

        # Set the last_form session variable to 'advanced'
        session['last_form'] = 'advanced'

        # Render the search results or display a message if no results found
        if len(resultTmp) > 0:
            advancedSearchResult = renderResult(resultTmp)
        else:
            advancedSearchResult = "No results found."

    # Render the search.html template with form data, search results, and other variables
    return render_template('search.html', simpleSearchForm=simpleSearchForm, simpleSearchResult=simpleSearchResult,
                           advancedSearchForm=advancedSearchForm, advancedSearchResult=advancedSearchResult,
                           last_form=session.get('last_form'), json_dict=json_dict)


# @app.route('/search/simple')
# def search_simple():
#    return os_manager.simple_search(config.get('Opensearch_Dashboard','default_index_name'), request.args.get('searchString')) #Hardcoded indexname
#
# @app.route('/search/advanced')
# def search_advanced():
#    search_info = json.loads(urllib.parse.unquote(request.args.get('searchString'))) #ToDo use Flask Forms
#    return os_manager.advanced_search(config.get('Opensearch_Dashboard', 'default_index_name'), search_info) #Hardcoded indexname

@app.route('/search/advanced_v2')
def advanced_search_v2():
    # Render the index1.html template for advanced search version 2
    return render_template('index1.html')

@app.route('/dashboards')
def dashboards():
    # Get the iframe data from the OS dashboard manager
    iframe_data = os_dashboard_manager.get_iframes()

    # Render the visualizations.html template, passing the iframe data
    return render_template('dashboards.html',iframe_data=iframe_data)


if __name__ == '__main__':
    # Entry point of the script

    # Run the Flask app
    # The following command starts the Flask application and launches a development server.
    # The app will listen for incoming requests on host '0.0.0.0' and port 8000.
    # The server will continue running until it is manually stopped.
    app.run(host='0.0.0.0', port=8000)

