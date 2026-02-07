import base64
import json
from typing import Any, Union
from dateutil import parser
from googlesearch import BeautifulSoup
import pyperclip
from datetime import datetime

class Utils(Exception):
    @staticmethod
    def copy_to_clipboard(txt: str) -> None:
        # Copy the text to the clipboard - @TODO: Add support for Windows and Linux
        #cmd='echo '+txt+'|pbcopy'
        #return subprocess.check_call(cmd, shell=True)
        pyperclip.copy(txt)
    
    @staticmethod
    def export_html_to_file(file_path: str, html_content: Any) -> None:
        soup: BeautifulSoup = Utils.get_html_document(html_content)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

    @staticmethod
    def format_date_string(date_string: str, output_format: str = "%m/%d/%Y %H:%M:%S") -> str:
        """
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'es_ES')
            except locale.Error:
                locale.setlocale(locale.LC_TIME, 'spanish')
        """
        try:
            return parser.parse(date_string).strftime(output_format)
        except ValueError as e:
            raise ValueError(f"Invalid Date string '{date_string}': {e}") from None

    @staticmethod
    def get_html_document(html_content: str) -> BeautifulSoup:
        """
        Get HMTL BeautifulSoup parsed document
        
        :param html_content: HTML string
        :type html_content: str
        :return: Document Object
        :rtype: BeautifulSoup
        """
        msg_str = base64.urlsafe_b64decode(html_content)
        soup: BeautifulSoup = BeautifulSoup(msg_str, 'lxml')
        return soup
        
    @staticmethod
    def get_time_zoned_epoch_datetime(
        date_time: str,
        time_zone: str = '-0600',
        format: str = '%Y/%m/%d %H:%M:%S %z'
    ) -> int:
        dt_obj = datetime.strptime(f'{date_time} {time_zone}', format)
        return dt_obj.timestamp() # * 1000

    @staticmethod
    def get_year_from_date(date_string: str) -> str:
        try:
            return parser.parse(date_string).year
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
    def load_json_file(file_path: str) -> Any:
        """
        Get Stored User Labels
        
        :return: Labels
        :rtype: Any
        """
        # @TODO: Manage with a DB
        return json.load(open(file_path))

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