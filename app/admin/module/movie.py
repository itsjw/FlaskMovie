# encoding: utf-8
import os

from flask import render_template, redirect, url_for, flash, current_app
from flask_wtf import csrf
from werkzeug.utils import secure_filename

from .. import admin
from ..forms import MovieForm
from app import db
from app.models import Movie
from app.utils import login_required_wraps, handle_filename


@admin.route("/movie-add/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def movie_add():
    form = MovieForm()

    if form.validate_on_submit():
        title = form.title.data
        count = Movie.query.filter_by(title=title).count()
        if count:
            flash("此电影已存在", "fail")
        else:
            logo = handle_filename(secure_filename(form.logo.data.filename))
            url = handle_filename(secure_filename(form.url.data.filename))
            kwargs = {k: y for k, y in form.data.items() if k not in ["logo", "url", "submit", "csrf_token"]}
            movie = Movie(logo=logo, url=url, **kwargs)

            form.logo.data.save(os.path.join(current_app.config["UPLOAD_DIR"], logo))
            form.url.data.save(os.path.join(current_app.config["UPLOAD_DIR"], url))

            db.session.add(movie)
            db.session.commit()
            flash("添加电影成功", "succeed")
            return redirect(url_for("admin.movie_add"))

    return render_template("admin/movie_add.html", form=form, title="添加电影", btn="添加")


@admin.route("/movie-delete/<int:movie_id>", methods=["POST"])
@login_required_wraps("admin", "admin.login")
def movie_delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("删除电影", "succeed")
    return redirect(url_for("admin.movie_list"))


@admin.route("/movie-edit/<int:movie_id>/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def movie_edit(movie_id):
    form = MovieForm()
    movie = Movie.query.get_or_404(movie_id)

    form.url.validators = []
    form.logo.validators = []
    if form.validate_on_submit():
        obj = Movie.query.filter_by(title=form.title.data).first()
        if obj and obj is not movie:
            flash("片名已存在", "fail")
        else:
            for k in form.data:
                if k in ["url", "logo"]:
                    filename = secure_filename(getattr(form, k).data.filename)
                    if filename:
                        filename = handle_filename(filename)
                        setattr(movie, k, filename)
                        getattr(form, k).data.save(os.path.join(current_app["UPLOAD_DIR"], filename))
                elif k not in ["submit", "csrf_token"]:
                    setattr(movie, k, getattr(form, k).data)

            db.session.add(movie)
            db.session.commit()
            flash("修改成功", "succeed")
            return redirect(url_for("admin.movie_list"))

    for k in form.data:
        if k not in ["submit", "csrf_token"]:
            getattr(form, k).data = getattr(movie, k)
    return render_template("admin/movie_add.html", title="编辑电影", btn="编辑", form=form, movie=movie)


@admin.route("/movie-list/")
@admin.route("/movie-list/<int:page>/")
@login_required_wraps("admin", "admin.login")
def movie_list(page=1):
    pagination = Movie.query.order_by(Movie.add_time.desc()).paginate(page=page, per_page=1)
    csrf_token = csrf.generate_csrf()
    return render_template("admin/movie_list.html", pagination=pagination, csrf_token=csrf_token)
