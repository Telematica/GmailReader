from typing import Union
import json

class Utils(Exception):
    @staticmethod
    def write_json_file(
        jsonStr: Union[str, object],
        filename='./secrets/labels.json'
    ) -> None:
        try:
            with open(filename, 'w') as file:
                if isinstance(jsonStr, str):
                    file.write(jsonStr)
                else:
                    json.dump(jsonStr, file, indent=4)
        except FileNotFoundError:
            raise FileNotFoundError(f"The directory for the file {filename} does not exist.")
        except IOError as e:
            raise IOError(f"An error occurred while writing to the file {filename}: {e}")
        except Exception as error:
            raise Exception(f"{error.__class__}: {error}") from None

    @staticmethod
    def is_valid_json(jsonFile: str) -> bool:
        try:
            json.loads(open(jsonFile).read())
        except ValueError as e:
            return False
        return True