import json

import requests
from pathlib import Path


# telegram functionalities are in this class

class Bot:
    __link__ = "https://api.telegram.org/bot{Token}/"
    __offset__ = 0

    def __init__(self, token):
        self.Token = token
        self.__link__ = self.__link__.format(Token=token)
        if Path('offset.txt').is_file():
            with open('offset.txt', 'r') as reader:
                self.__offset__ = int(reader.read())
        else:
            self.__offset__ = 0

    def send_message(self, chat_id: int, text: str, disable_web_page_preview: bool = False, reply_markup: dict = None):
        link = self.__link__ + "sendMessage"

        params = {
            'chat_id': chat_id,
            'text': text,
            'disable_web_page_preview': disable_web_page_preview
        }

        if reply_markup is not None:
            params['reply_markup'] = json.dumps(reply_markup)

        response = requests.get(link, params=params)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception(response.json())

    def edit_message(self, chat_id: int, message_id: int, text: str, disable_web_page_preview: bool = False,
                     reply_markup: dict = None):
        link = self.__link__ + "editMessageText"

        params = {
            'chat_id': chat_id,
            'message_id':message_id,
            'text': text,
            'disable_web_page_preview': disable_web_page_preview
        }

        if reply_markup is not None:
            params['reply_markup'] = json.dumps(reply_markup)

        response = requests.get(link, params=params)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception(response.json())

    # returns a Update object
    def get_updates(self, limit: int, timeout: int = None, allowed_updates: list = None):
        link = self.__link__ + "getUpdates"

        # add offset and limit
        params = {
            'offset': self.__offset__,
            'limit': limit
        }

        if timeout is not None:
            params['timeout'] = timeout

        if allowed_updates is not None:
            params['allowed_updates'] = allowed_updates

        response = requests.get(link, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data['result']) > 0:
                self.__offset__ = data['result'][-1]['update_id'] + 1

            # save offset in case of crash
            with open('offset.txt', 'w') as writer:
                writer.write(str(self.__offset__))

            return data
        else:
            raise Exception(response.json())
