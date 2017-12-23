# encoding: utf-8
from flask import render_template, redirect, url_for, request, session, flash, abort

from . import admin
from .forms import LoginForm, PasswordForm
from app import db
from app.models import Auth, Admin, AdminLog
from app.utils import login_required_wraps

from .module import *


def admin_auth(func):
    from functools import wraps
    @wraps(func)
    def inner(*args, **kwargs):
        import json
        admin = Admin.query.get_or_404(int(session.get("admin_id", 0)))
        if admin.is_super != 0:
            auths = json.loads(admin.role.auths)
            urls = [obj.url for obj in Auth.query.filter(Auth.id.in_(auths)).all()]

            if str(request.url_rule) not in urls:
                abort(404)

        return func(*args, **kwargs)

    return inner


@admin.context_processor
def tpl_extra():
    from datetime import datetime
    return {"datetime": datetime.now().strftime("%Y-%m-%d")}


@admin.route("/")
@login_required_wraps("admin", "admin.login")
def index():
    return render_template("admin/index.html")


@admin.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        log = AdminLog(admin_id=session.get("admin_id"), ip=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin.route("/logout/")
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))


@admin.route("/pwd/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def pwd():
    form = PasswordForm()
    if form.validate_on_submit():
        from werkzeug.security import generate_password_hash
        admin_obj = Admin.query.filter_by(name=session.get("admin")).first()
        admin_obj.password = generate_password_hash(form.new_password.data)
        db.session.add(admin)
        db.session.commit()
        flash("修改成功，请重新登录", "succeed")
        return redirect(url_for("admin.logout"))
    return render_template("admin/pwd.html", form=form)
