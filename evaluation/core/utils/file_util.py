import os

def get_project_related_file_path(project_path, file_path):
    return os.path.join(project_path, file_path)