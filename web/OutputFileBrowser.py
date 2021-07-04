import os
import posixpath
import time
from urllib import parse

from flask import render_template, send_from_directory

# 共享文件夹的根目录
root_dir = os.getcwd()


def out_put(params):
    return document(params)


def document(subdir: str):
    if subdir is None or subdir == '':
        # 名字为空
        subdir = ''
    current_dir = _translate_path(subdir)
    # 如果是文件，则下载
    if os.path.isfile(current_dir):
        return downloader(current_dir)
    # 非文件处理
    current_list = os.listdir(current_dir)
    contents = []
    for i in sorted(current_list):
        full_path = os.path.join(current_dir, i)
        link = subdir
        if not subdir.endswith('/'):
            link += '/'
        extra = ''
        if os.path.isdir(full_path):
            extra = '/'

        content = {'filename': i + extra,
                   'file_link': link + i,
                   'mtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.stat(full_path).st_mtime)),
                   'size': str(round(os.path.getsize(full_path) / (1024 * 1024), 2)) + 'MB'}
        contents.append(content)
    return render_template('OuputFileBrowser.html', contents=contents, subdir=subdir, ossep=os.sep)


def downloader(fullname):
    filename = fullname.split(os.sep)[-1]
    dirpath = fullname[:-len(filename)]
    return send_from_directory(dirpath, filename, as_attachment=True)


def _translate_path(path):
    """Translate a /-separated PATH to the local filename syntax.

    Components that mean special things to the local file system
    (e.g. drive or directory names) are ignored.  (XXX They should
    probably be diagnosed.)

    """
    # abandon query parameters
    path = path.split('?', 1)[0]
    path = path.split('#', 1)[0]
    # Don't forget explicit trailing slash when normalizing. Issue17324
    trailing_slash = path.rstrip().endswith('/')
    try:
        path = parse.unquote(path, errors='surrogatepass')
    except UnicodeDecodeError:
        path = parse.unquote(path)
    path = posixpath.normpath(path)
    words = path.split('/')
    words = filter(None, words)
    path = root_dir
    for word in words:
        if os.path.dirname(word) or word in (os.curdir, os.pardir):
            # Ignore components that are not a simple file/directory name
            continue
        path = os.path.join(path, word)
    if trailing_slash:
        path += '/'
    return path
