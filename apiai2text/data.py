from functools import reduce
from typing import Dict, Tuple, List

import os
import zipfile
import json

from urllib.parse import urlparse

class APIAIIntent(object):
    
    def __init__(self, jc):
        self.id = jc["id"]
        self.name = jc["name"]
        self.auto = bool(jc["name"])
        self.contexts = jc["contexts"]
        self.templates = jc["templates"]
        self.user_says = list(map(lambda x: APIAIIntent.UserSays(x), jc["userSays"]))
        self.responses = list(map(lambda x: APIAIIntent.Responses(x), jc["responses"]))

    class UserSays(object):

        def __init__(self, jc):
            self.id = jc["id"]
            self.is_template = bool(jc["isTemplate"])
            self.count = int(jc["count"])
            self.data = list(map(lambda x: APIAIIntent.UserSaysData(x), jc["data"]))

    class UserSaysData(object):

        def __init__(self, jc):
            self.text = jc["text"]
            # self.meta = jc["meta"]
            # self.alias = jc["alias"]
            # self.user_defined = jc["userDefined"]

    class Responses(object):

        def __init__(self, jc):
            # self.action = jc["action"]
            self.reset_contexts = jc["resetContexts"]
            self.affected_contexts = list(map(lambda x: {"name": x["name"], "lifespan": x["lifespan"]}, jc["affectedContexts"]))
            self.parameters = list(map(lambda x: APIAIIntent.Parameters(x), jc["parameters"]))
            self.messages = list(map(lambda x: self.instantiate_message(x), jc["messages"]))

        def instantiate_message(self, jc_message):
            if jc_message["type"] == 0:
                return APIAIIntent.TextResponse(jc_message)
            if jc_message["type"] == 3:
                return APIAIIntent.ImageResponse(jc_message)
            if jc_message["type"] == 1:
                return APIAIIntent.CardResponse(jc_message)
            if jc_message["type"] == 2:
                return APIAIIntent.QuickReplyes(jc_message)

    class Parameters(object):

        def __init__(self, jc):
            self.name = jc["name"]
            self.value = jc["value"]
            self.default_value = jc["defaultValue"]
            self.required = bool(jc["required"])
            self.data_type = jc["dataType"]
            self.prompts = jc["prompts"]
            self.is_list = bool(jc["isList"])

    class TextResponse(object):

        def __init__(self, jc):
            self.type = "TEXT_RESPONSE"
            if isinstance(jc["speech"], str):
                self.speech = [jc["speech"]]
            else:
                self.speech = jc["speech"]
    
    class ImageResponse(object):

        def __init__(self, jc):
            self.type = "IMAGE_RESPONSE"
            self.image_url = jc["imageUrl"]

    class CardResponse(object):

        def __init__(self, jc):
            self.type = "CARD_RESPONSE"
            self.title = jc["title"]
            self.subtitle = jc["subtitle"]
            # TODO: Buttons

    class QuickReplyes(object):

        def __init__(self, jc):

            self.type = "QUICK_REPLY"
            self.title = jc["title"]
            self.replies = jc["replies"]

class APIAITextIntent(object):

    def __init__(self, name: str, json_content: dict):
        """
        Constructor
        :param name: The intent name.
        :param json_content: The raw JSON content of the intent.
        """
        self.api_ai_intent = APIAIIntent(json_content)
        print(self.api_ai_intent)
        self.answers, self.quick_answers = APIAITextIntent.find_text_answer(self.api_ai_intent)
        self.name = name
        self.user_says = APIAITextIntent.find_user_say(json_content)

    @staticmethod
    def find_quick_answers(messages: List):
        """
        Extract the list of quick answer associated to the given intent.
        :param messages: The list of messages in the intent.
        :type messages: list
        """
        result = []
        for m in messages:
            if m.type == "QUICK_REPLY":
                result += m.replies
        #return [qa for m in messages if "replies" in m
        #        for qa in m["replies"]]
        return result

    @staticmethod
    def find_text_answer(apiai_intent: APIAIIntent) -> Tuple[list, list]:
        """
        Extract information about the bot's answers and questions from
        the JSON dictionary passed as an argument.
        """
        # Answers are in responses[x].messages[y].speech[z]
        # or responses[x].messages[y].title
        # or responses[x].messages[y].imageUrl (if image)
        # title is a str
        # speech can be a str or a list.
        responses = apiai_intent.responses
        messages = [x for r in responses for x in r.messages]
        # messages = reduce(lambda x, y: x + y["messages"], responses, [])

        def reduce_speech(x: list, y: dict):
            if y.type == "TEXT_RESPONSE":
                return x + y.speech
            if y.type == "CARD_RESPONSE":
                return x + [y.title]
            if y.type == "IMAGE_RESPONSE":
                return x + [y.image_url]
            # WARN: Silently do nothing.
            return x

        speech = reduce(reduce_speech, messages, [])
        quick_answers = APIAITextIntent.find_quick_answers(messages)

        return speech, quick_answers

    @staticmethod
    def is_image_url(s):
        """
        Check if the string is an url to an image.
        """
        # FIXME: Check for an image, not a generic URL.
        parsed = urlparse(s)
        return parsed.scheme != '' and parsed.netloc != ''

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
        return pretty_print(all_intents)

    except IOError as e:
        print(e)
        exit(-1)


def pretty_print(all_intents: List[APIAITextIntent]):
    """
    Generate a pretty print of the conversion output.
    """
    result = ""
    for i in all_intents:
        result += '\n# Intent: {}\n\n'.format(i.name)
        result += "## User Says:\n\n"
        for s in i.user_says:
            result += " - {}\n".format(s)
        result += "\n## Agent Responses\n\n"
        for a in i.answers:
            if type(a) is str:
                if APIAITextIntent.is_image_url(a):
                    result += " 1. <img style=\"width: 250px;\" src=\"{}\">\n".format(
                        a)
                else:
                    result += " 1. {}\n".format(a)
            else:
                if len(a) > 0:
                    result += " 1. *Alternatives:*\n"
                    for element in a:
                        if element is not "":
                            result += "     - {}\n".format(element)
        if len(i.quick_answers) > 0:
            result += "\n## Possible User Answers\n\n"
            for qa in i.quick_answers:
                result += " - {}\n".format(qa)
    return result
