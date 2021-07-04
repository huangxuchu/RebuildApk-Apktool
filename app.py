"""
author: Huangxuchu
version:
date: 2021/7/2
description: 
"""

from flask import Flask, request

import Constants
import main
from config import Config
from web import index, OutputFileBrowser

app = Flask(__name__)
app.config.from_object(Config)


@app.before_request
def before_request():
    if request.path.startswith('/output/'):
        return handle_out_put(request.path)
    else:
        return None


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    return index.handle(request)


@app.route('/output')
def oup_put():
    return handle_out_put(request.path)


def handle_out_put(params):
    return OutputFileBrowser.out_put(params)


if __name__ == '__main__':
    main.check_and_mkdir(Constants.PATH_MATERIAL)
    main.check_and_mkdir(Constants.PATH_TEMP)
    main.check_and_mkdir(Constants.PATH_OUTPUT)
    app.run()
