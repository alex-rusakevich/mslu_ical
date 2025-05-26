import toml


def get_project_version(pyproject_path='pyproject.toml'):
    pyproject_data = toml.load(pyproject_path)
    version = pyproject_data['tool']['poetry']['version']
    return version

