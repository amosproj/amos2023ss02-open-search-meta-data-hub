from datetime import datetime


# The DataTypes class encapsulates the data_types dictionary.
# It provides a getter method (get_data_type) and a setter method (set_data_type)
# for retrieving and updating the type of each key.

# You can create an instance of the DataTypes class (data_types_obj)
# and then use its getter and setter methods to access and modify the data type for each key.
# The example usage demonstrates how to get the data type for the 'FileName' key and set a new data type for it.

# Feel free to modify the code or extend the class with additional functionality as per your requirements.
class DataTypes:
    def __init__(self):

        self._data_types = {
            'FileName': {"type": "text"},
            'FileSize': {"type": "integer"},
            'MIMEType': {"type": "text"},
            'FileInodeChangeDate': {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis",
                "value": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            },
            'SourceFile': {"type": "text"}
        }

    def get_data_types(self) -> dict:
        """ returns the whole data_types dictionary """
        return self._data_types

    def get_data_type(self, field: str) -> str:
        """Get the data type for a given field."""
        try:
            return self._data_types[field]['type']
        except KeyError:
            print("Unknown field")

    def set_data_type(self, field: str, data_type: str):
        """Set the data type for a given field."""
        self._data_types[field]['type'] = data_type
