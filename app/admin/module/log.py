# encoding: utf-8
from flask import render_template

from .. import admin
from app.models import OperationLog, AdminLog, UserLog
from app.utils import login_required_wraps


@admin.route("/operation-log/")
@admin.route("/operation-log/<int:page>/")
@login_required_wraps("admin", "admin.login")
def operation_log(page=1):
    pagination = OperationLog.query.order_by(OperationLog.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/operation_log.html", pagination=pagination)


@admin.route("/admin-login-log/")
@admin.route("/admin-login-log/<int:page>/")
@login_required_wraps("admin", "admin.login")
def admin_login_log(page=1):
    pagination = AdminLog.query.order_by(AdminLog.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/admin_login_log.html", pagination=pagination)


@admin.route("/user-login-log/")
@admin.route("/user-login-log/<int:page>/")
@login_required_wraps("admin", "admin.login")
def user_login_log(page=1):
    pagination = UserLog.query.order_by(UserLog.add_time.desc()).paginate(page=page, per_page=2)
    return render_template("admin/user_login_log.html", pagination=pagination)
