import os
import sys
import pickle


class Import:

    def __init__(self, successful, version, files_in_os, files_in_mdh):
        """
          Represents an import operation.

          :param successful: A boolean indicating whether the import operation was successful.
          :param version: An integer representing the version of the import.
          :param files_in_os: An integer indicating the number of files in the operating system.
          :param files_in_mdh: An integer indicating the number of files in the MDH.
          """

        self._successful = successful
        self._version = version
        self._files_in_os = files_in_os
        self._files_in_mdh = files_in_mdh

    # Getters and setters for class properties
    @property
    def successful(self):
        """
             Get the success status of the import operation.

             :return: A boolean indicating whether the import operation was successful.

      """
        return self._successful

    @property
    def version(self):
        """
        Get the version of the import.

        :return: An integer representing the version of the import.
        """
        return self._version

    @property
    def files_in_os(self):
        """
               Get the number of files in the operating system.

               :return: An integer indicating the number of files in the operating system.
               """
        return self._files_in_os

    @property
    def files_in_mdh(self):
        """
              Get the number of files in the MDH.

              :return: An integer indicating the number of files in the MDH.
              """
        return self._files_in_mdh

    @successful.setter
    def successful(self, value):
        """
              Set the success status of the import operation.

              :param value: A boolean indicating whether the import operation was successful.
              """
        self._successful = value

    @version.setter
    def version(self, value):
        """
               Set the version of the import.

               :param value: An integer representing the version of the import.
               """
        self._version = value

    @files_in_os.setter
    def files_in_os(self, value):
        """
           Set the number of files in the operating system.

           :param value: An integer indicating the number of files in the operating system.
           """
        self._files_in_os = value

    @files_in_mdh.setter
    def files_in_mdh(self, value):
        """
              Set the number of files in the MDH.

              :param value: An integer indicating the number of files in the MDH.
              """
        self._files_in_mdh = value


class ImportControl:

    def __init__(self):
        """
           Controls the import operations and manages the import state.

           The path attribute specifies the file path where the import state is stored.
           """
        self.path = 'import.dictionary'

    def create_import(self, files_in_os, files_in_mdh):
        """
             Creates a new import state with the given files_in_os and files_in_mdh values.

             :param files_in_os: An integer indicating the number of files in the operating system.
             :param files_in_mdh: An integer indicating the number of files in the MDH.
             """
        new_import = Import(successful=False, version=1, files_in_os=0, files_in_mdh=100)
        self._write(new_import)

    def update_import(self, imported_files):
        """
                Updates the import state with the given files_in_os value.

                :param files_in_os: An integer indicating the number of files in the operating system.
                """
        last_import: Import = self._get_last_import()
        if last_import is not None:
            updated_import = Import(successful=True, version=last_import.version,
                                    files_in_os=last_import.files_in_os + imported_files,
                                    files_in_mdh=last_import.files_in_mdh)
            self._write(updated_import)

    def last_import_successful(self):
        """
             Checks if the last import was successful.

             :return: A boolean indicating whether the last import was successful.
             """
        last_import: Import = self._get_last_import()
        if last_import is not None:
            return last_import.successful
        else:
            return False

    def _get_last_import(self):
        """
             Retrieves the last import state from the file.

             :return: The last Import object if it exists, None otherwise.
             """
        try:
            with open(self.path, 'rb') as import_dictionary_file:
                last_import = pickle.load(import_dictionary_file)
                return last_import
        except EOFError:
            return None

    def _write(self, new_import):
        """
             Writes the new import state to the file.

             :param new_import: The Import object to be written to the file.
             """
        with open(self.path, 'wb') as import_dictionary_file:
            # Step 3
            pickle.dump(new_import, import_dictionary_file)
        pass


# Usage example

# Create an instance of ImportControl
ic = ImportControl()

# Create an initial import with files_in_os = 0 and files_in_mdh = 0
ic.create_import(0, 0)

# Update the import with files_in_os = 0
ic.update_import(0)

# Check if the last import was successful
print(ic.last_import_successful())

"""

Files in MDH: 1000 

1. Import: Limit = 150,
-> files downloaded = 150
-> offset = 0
-> Import-Control:
    - files in OS: 150 
    - files in MDH: 1000

2. Import: Limit = 100
-> files downloaded = 250 
-> offset = 150 
-> import control:
    - files in OS: 250
    - files in MDH: 1000
    
3. Import: Limit = False
-> files downloaded = 1000
-> offset = 250
-> import control:
    - files in OS: 1000
    - files in MDH: 1000

"""
