import json
from pathlib import Path


class MockLoader:

    """
    Load a file from the mock_data directory
    """
    @staticmethod
    def load(file_path, parse_json=True):
        path = Path(__file__).parent.joinpath(file_path)
        if path.exists():
            with open(path, 'r') as file:
                if parse_json:
                    return json.load(file)
                else:
                    return file.read()
        return None