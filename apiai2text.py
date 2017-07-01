# -*- coding: utf-8 -*-
"""
Convert API.AI export .zip into readable text.
"""

from typing import Dict, Tuple, List

import os
import zipfile
import json

import argparse

from apiai2text.data import APIAITextIntent


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
