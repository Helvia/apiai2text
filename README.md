# ApiAI2Text

Python script for converting the API.AI zip export file into human readable text files (default: Markdown).

Exporting an API.AI agent in readable format is useful for making the bot text and behavior accessible to other non-tech people, proofreading, and general design.

## Usage

```
usage: apiai2text.py [-h] input_file

positional arguments:
  input_file  The input .zip file

optional arguments:
  -h, --help  show this help message and exit
```

Output is generated on `stdout`. Direct export to file will be introduced in alater version.