import yaml


class FileIO(object):
    def __init__(self):
        pass

    def _parse_yaml(self, config_file):
        with open(config_file, "r") as file:
            return yaml.safe_load(file)

    def _return_file_contents_as_string(self, filename):
        file = open(filename, "r")
        data = file.read()
        file.close()
        return data
