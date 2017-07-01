# ApiAI2Text

Python script for converting the API.AI zip export file into human readable text files (default: Markdown).

Exporting an API.AI agent in readable format is useful for making the bot text and behavior accessible to other non-tech people, proofreading, and general design.

## Prerequisite

If you want to run the REST service and have an online preview of your agent, you need the following Python packages.
They are not required if you run only command line interface.

```commandline
pip install flask
pip install markdown2
pip install requests
```

## Usage

### Standard Usage

```
usage: apiai2text.py [-h] input_file

positional arguments:
  input_file  The input .zip file

optional arguments:
  -h, --help  show this help message and exit
```

Output is generated on `stdout`. Direct export to file will be introduced in alater version.

### REST Application

This script can also be run in server mode allowing live fetching and preview from API.AI.
In this case, just add the `--rest` flag to the script.