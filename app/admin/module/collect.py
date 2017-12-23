# encoding: utf-8
from flask import render_template, redirect, url_for, flash, request

from .. import admin
from app import db
from app.models import MovieCollect
from app.utils import login_required_wraps


@admin.route("/collect-list/")
@admin.route("/collect-list/<int:page>/")
@login_required_wraps("admin", "admin.login")
def collect_list(page=1):
    pagination = MovieCollect.query.order_by(MovieCollect.add_time.desc()).paginate(page=page, per_page=5)
    return render_template("admin/collect_list.html", pagination=pagination)


@admin.route("/collect-delete/<int:collect_id>", methods=["POST"])
@login_required_wraps("admin", "admin.login")
def collect_delete(collect_id):
    collect = MovieCollect.query.get_or_404(collect_id)
    db.session.delete(collect)
    db.session.commit()
    flash("删除收藏", "succeed")
    page = request.args.get("page", 1)
    return redirect(url_for("admin.collect_list", page=page))
