import os
import sys
import pickle


class Import:

    def __init__(self, successful, version, files_in_os, files_in_mdh):
        self._successful = successful
        self._version = version
        self._files_in_os = files_in_os
        self._files_in_mdh = files_in_mdh

    @property
    def successful(self):
        return self._successful

    @property
    def version(self):
        return self._version

    @property
    def files_in_os(self):
        return self._files_in_os

    @property
    def files_in_mdh(self):
        return self._files_in_mdh

    @successful.setter
    def successful(self, value):
        self._successful = value

    @version.setter
    def version(self, value):
        self._version = value

    @files_in_os.setter
    def files_in_os(self, value):
        self._files_in_os = value

    @files_in_mdh.setter
    def files_in_mdh(self, value):
        self._files_in_mdh = value


class ImportControl:

    def __init__(self):
        self.path = 'import.dictionary'

    def create_import(self, files_in_os, files_in_mdh):
        new_import = Import(successful=False, version=1, files_in_os=0, files_in_mdh=100)
        self._write(new_import)

    def update_import(self, imported_files):
        last_import: Import = self._get_last_import()
        if last_import is not None:
            updated_import = Import(successful=True, version=last_import.version,
                                files_in_os=last_import.files_in_os+imported_files, files_in_mdh=last_import.files_in_mdh)
            self._write(updated_import)

    def get_last_import(self):
        last_import: Import = self._get_last_import()
        if last_import is not None:
            return last_import
        else:
            return None

    def _get_last_import(self):
        try:
            with open(self.path, 'rb') as import_dictionary_file:
                last_import = pickle.load(import_dictionary_file)
                return last_import
        except EOFError:
            return None

    def _write(self, new_import):
        with open(self.path, 'wb') as import_dictionary_file:
            # Step 3
            pickle.dump(new_import, import_dictionary_file)
        pass

ic = ImportControl()
ic.create_import(0, 0)
ic.update_import(0)
print(ic.last_import_successful())


