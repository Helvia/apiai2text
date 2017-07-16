import requests
import json
from flask import Flask, request, render_template, Markup

from apiai2text.data import convert_zip_file, APIAITextIntent, pretty_print
import markdown2
import time

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/')
def hello_world():
    return render_template('index.html', name='Hello World!')


@app.route('/agent', methods=['GET'])
def view_agent():
    bar = request.args.to_dict()
    if "apiai_token" in bar:
        intents = get_all_intents(bar["apiai_token"])
        text = pretty_print(intents)
    else:
        text = convert_zip_file(app.config["file"])
    return render_template('agent.html', content=Markup(markdown2.markdown(text)))


def get_all_intents(dev_token):
    url = "https://api.api.ai/v1/intents?v=20150910"
    headers = {"Authorization": "Bearer {}".format(dev_token)}
    r = requests.get(url, headers=headers)
    json_content = r.json()
    intents_ids = [(x["name"], x["id"]) for x in json_content]
    all_intents = []
    for (name, iid) in intents_ids:
        url = "https://api.api.ai/v1/intents/{}?v=20150910".format(iid)
        r = requests.get(url, headers=headers)
        print(str(r))
        time.sleep(1.1) # TODO: Fix this delay in a good way.
        all_intents.append(APIAITextIntent(name, r.json()))
    return all_intents
