# encoding: utf-8
from datetime import datetime
from functools import wraps
from uuid import uuid4
from stat import S_IRWXU, S_IRWXG, S_IRWXO
import os

from flask import session, redirect, url_for, request


def login_required_wraps(session_key, url):
    def login_required(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if session_key not in session:
                return redirect(url_for(url, next=request.url))
            return func(*args, **kwargs)

        return inner

    return login_required


def handle_filename(filename):
    name_extension = os.path.splitext(filename)[-1]
    if name_extension:
        return datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid4().hex) + name_extension
    return datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid4().hex) + "." + filename


def create_upload_dir(path):
    UPLOAD_DIR = os.path.join(path, "static", "upload")
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        os.chmod(UPLOAD_DIR, S_IRWXU + S_IRWXG + S_IRWXO)
    return UPLOAD_DIR
