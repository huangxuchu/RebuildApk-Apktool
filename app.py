"""
author: Huangxuchu
version:
date: 2021/7/2
description: 
"""

from flask import Flask, request

import Constants
import config
import main
from config import FlaskConfig
from web import index, OutputFileBrowser

app = Flask(__name__)
app.config.from_object(FlaskConfig)


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


from gevent import pywsgi

if __name__ == '__main__':
    main.check_and_mkdir(Constants.PATH_MATERIAL)
    main.check_and_mkdir(Constants.PATH_TEMP)
    main.check_and_mkdir(Constants.PATH_OUTPUT)
    if FlaskConfig.DEBUG:
        app.run()
    else:
        server = pywsgi.WSGIServer((config.HOST, config.PORT), app)
        server.serve_forever()
