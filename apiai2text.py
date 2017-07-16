# -*- coding: utf-8 -*-
"""
Convert API.AI export .zip into readable text.
"""

from typing import Dict, Tuple, List

import os
import argparse

from apiai2text.data import convert_zip_file
from apiai2text.rest import app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert API.AI export zip in text format.")
    parser.add_argument("input_file", type=str, help="The input .zip file")
    parser.add_argument("--rest", action='store_true', help="Start a live HTTP viewer.")
    args = parser.parse_args()

    if args.rest:
        app.config["file"] = args.input_file
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0',port=port)
    else:
        print(convert_zip_file(args.input_file))
