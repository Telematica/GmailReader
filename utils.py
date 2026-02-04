from distutils import cmd
import json
from typing import Union
from dateutil import parser
import pyperclip

class Utils(Exception):
    @staticmethod
    def copy_to_clipboard(txt: str) -> None:
        # Copy the text to the clipboard
        #todo: Add support for Windows and Linux
        pyperclip.copy(txt)
        #cmd='echo '+txt+'|pbcopy'
        #return subprocess.check_call(cmd, shell=True)

    @staticmethod
    def format_date_string(date_string: str, output_format: str = "%m/%d/%Y %H:%M:%S") -> str:
        try:
            return parser.parse(date_string).strftime(output_format)
        except ValueError as e:
            raise ValueError(f"Invalid Date string '{date_string}': {e}") from None
    
    @staticmethod
    def is_valid_json(jsonFile: str) -> bool:
        try:
            json.loads(open(jsonFile).read())
        except ValueError as e:
            return False
        return True

    @staticmethod
    def write_json_file(
        json_str: Union[str, object],
        filename='./secrets/labels.json'
    ) -> None:
        try:
            with open(filename, 'w') as file:
                if isinstance(json_str, str):
                    file.write(json_str)
                else:
                    json.dump(json_str, file, indent=4)
        except FileNotFoundError:
            raise FileNotFoundError(f"The directory for the file {filename} does not exist.")
        except IOError as e:
            raise IOError(f"An error occurred while writing to the file {filename}: {e}")
        except Exception as error:
            raise Exception(f"{error.__class__}: {error}") from None
