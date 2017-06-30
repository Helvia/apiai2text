# -*- coding: utf-8 -*-
"""
Convert API.AI export .zip into readable text.
"""

from typing import Dict, Tuple, List

import os
import sys
import zipfile
import json

import argparse

from functools import reduce


class APIAITextIntent(object):
    def __init__(self, name: str, json_content: dict):
        """
        Constructor
        :param name: The intent name. 
        :param json_content: The raw JSON content of the intent.
        """
        self.answers, self.quick_answers = APIAITextIntent.find_text_answer(json_content)
        self.name = name
        self.user_says = APIAITextIntent.find_user_say(json_content)

    @staticmethod
    def find_quick_answers(messages):
        """
        Extract the list of quick answer associated to the given intent.
        :param messages: The list of messages in the intent.
        :type messages: list
        """
        return [qa for m in messages if "replies" in m
                for qa in m["replies"]]

    @staticmethod
    def find_text_answer(json_dict: dict) -> Tuple[list, list]:
        """
        Extract information about the bot's answers and questions from 
        the JSON dictionary passed as an argument.
        """
        # Answers are in responses[x].messages[y].speech[z]
        # or responses[x].messages[y].title
        # title is a str
        # speech can be a str or a list.
        responses = json_dict["responses"]
        messages = reduce(lambda x, y: x + y["messages"], responses, [])

        def reduce_speech(x: list, y: dict):
            if "speech" in y:
                return x + [y["speech"]]
            if "title" in y:
                return x + [y["title"]]
            # WARN: Silently do nothing.
            return x

        speech = reduce(reduce_speech, messages, [])
        quick_answers = APIAITextIntent.find_quick_answers(messages)

        return speech, quick_answers

    @staticmethod
    def find_user_say(json_dict):
        """
        Extract information about the users' answers and questions from
        the JSON dictionary passed as an argument.
        """
        # user text is in userSays[x].data[x].text
        userSays = json_dict["userSays"]
        data = reduce(lambda x, y: x + y["data"], userSays, [])
        texts = reduce(lambda x, y: x + [y["text"]], data, [])
        return texts


def convert_zip_file(zip_archive_name: str):
    """
    The main script function.
    """
    try:
        archive = zipfile.ZipFile(zip_archive_name, "r")

        all_intents = []
        for name in archive.namelist():
            if name.startswith('intents/'):
                if not os.path.isdir(name):
                    with archive.open(name) as f:
                        json_content = json.loads(f.read())
                        all_intents.append(APIAITextIntent(name, json_content))
        pretty_print(all_intents)

    except IOError as e:
        print(e)
        exit(-1)


def pretty_print(all_intents: List[APIAITextIntent]):
    """
    Generate a pretty print of the conversion output.
    """
    for i in all_intents:
        print('# Intent: {}'.format(i.name))
        print("## User Says:")
        for s in i.user_says:
            print(" - {}".format(s))
        print("## Answers")
        for a in i.answers:
            if type(a) is str:
                print(" 1. {}".format(a))
            else:
                if len(a) > 0:
                    print(" 1. *Alternatives:*")
                    for element in a:
                        if element is not "":
                            print("     - {}".format(element))
        if len(i.quick_answers) > 0:
            print("## Possible User Answers")
            for qa in i.quick_answers:
                print(" - {}".format(qa))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert API.AI export zip in text format.")
    parser.add_argument("input_file", type=str, help="The input .zip file")
    args = parser.parse_args()

    convert_zip_file(args.input_file)
