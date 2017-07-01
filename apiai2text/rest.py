from flask import Flask, request

from apiai2text.data import convert_zip_file
import markdown2

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/agent', methods=['GET'])
def view_agent():
    bar = request.args.to_dict()
    text = convert_zip_file(app.config["file"])
    return markdown2.markdown(text)