import json


# Function to retrieve the last imported entry's identifier or timestamp from the recovery file
def get_last_imported_entry():
    try:
        with open('recovery.json', 'r') as file:
            data = json.load(file)
            return data['last_imported_entry']
    except FileNotFoundError:
        return None


# Function to update the last imported entry in the recovery file
def update_last_imported_entry(entry):
    data = {'last_imported_entry': entry}
    with open('recovery.json', 'w') as file:
        json.dump(data, file)

