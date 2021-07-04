import os

from flask import render_template
from werkzeug.utils import secure_filename

import Constants
import DateUtils
from main import Main

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'json', 'apk', 'xls', 'xlsx'}


def handle(request):
    if request.method == 'POST':
        date_time = DateUtils.date_time()
        upload_succeed = False
        request_files = request.files
        if handle_post('apkFile', date_time, request_files):
            upload_succeed = handle_post('excelFile', date_time, request_files)
        if upload_succeed:
            Main().start(date_time)
            return "上传成功，开始任务 task=" + date_time + f'<p>查看你的任务结果：<a href=/output/{date_time} target="right_body">{request.base_url}output/{date_time} </a></p>'
        else:
            return "上传失败"
    else:
        return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def handle_post(key, task_id, request_files):
    # check if the post request has the file part
    if key not in request_files:
        return False
    file = request_files[key]
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return False
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        task_path = os.path.join(Constants.PATH_MATERIAL, task_id)
        if not os.path.exists(task_path):
            os.mkdir(task_path)
        file.save(os.path.join(task_path, filename))
        return True
    else:
        return False
