from functools import reduce
from typing import Dict, Tuple, List

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
