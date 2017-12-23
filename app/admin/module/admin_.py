# encoding: utf-8
from flask import render_template, redirect, url_for, flash

from .. import admin
from ..forms import AdminForm
from app import db
from app.models import Admin
from app.utils import login_required_wraps


@admin.route("/admin-add/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def admin_add():
    form = AdminForm()
    if form.validate_on_submit():
        count = Admin.query.filter_by(name=form.name.data).count()
        if count:
            flash("此管理员已存在", "fail")
        else:
            from werkzeug.security import generate_password_hash
            admin_obj = Admin(
                name=form.name.data,
                password=generate_password_hash(form.password.data),
                role_id=form.role_id.data,
                is_super=1
            )
            db.session.add(admin_obj)
            db.session.commit()
            flash("添加管理员", "succeed")
            return redirect(url_for("admin.admin_add"))
    return render_template("admin/admin_add.html", form=form)


@admin.route("/admin-list/")
@admin.route("/admin-list/<int:page>/")
@login_required_wraps("admin", "admin.login")
def admin_list(page=1):
    pagination = Admin.query.order_by(Admin.add_time.desc()).paginate(page=page, per_page=2)
    return render_template("admin/admin_list.html", pagination=pagination)
