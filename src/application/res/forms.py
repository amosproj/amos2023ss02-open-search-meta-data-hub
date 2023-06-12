from flask_wtf import FlaskForm
from backend.opensearch_api import OpenSearchManager

from wtforms import *

os_manager: OpenSearchManager = OpenSearchManager()
index_name = 'amoscore'

class SearchForm:
    fields = os_manager.get_all_fields(index_name=index_name)
    search_field = SelectField(choices=fields)
    pass

class SearchTextForm(FlaskForm, SearchForm):
    search_text = StringField()
    operators = SelectField(choices=["EQUALS", "EQUALS_NOT"])

class SearchNumberForm(FlaskForm, SearchForm):
    search_number = FloatField()
    operators = SelectField(choices=["EQUALS", "EQUALS_NOT", "GREATER_THAN", "LESSER_THAN"])

class SearchDateForm(FlaskForm, SearchForm):
    search_date = DateField()
    operators = SelectField(choices=["EQUALS", "EQUALS_NOT", "GREATER_THAN", "LESSER_THAN"])