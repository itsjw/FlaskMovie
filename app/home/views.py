# encoding: utf-8
import os
from uuid import uuid4
from datetime import datetime

from flask import render_template, redirect, url_for, flash, session, request, current_app, jsonify, Response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy import and_
from flask_wtf import csrf

from . import home
from .forms import RegisterForm, LoginForm, UserDetailForm, PasswordForm, CommentForm
from app import db, redis
from app.models import User, UserLog, Preview, Tag, Movie, Comment, MovieCollect
from app.utils import login_required_wraps, handle_filename


@home.route("/")
@home.route("/<int:page>/")
def index(page=1):
    args = dict(
        tag=request.args.get("tag", 0),
        star_level=request.args.get("star_level", 0),
        release_time=request.args.get("release_time"),
        play_num=request.args.get("play_num", 0),
        comment_num=request.args.get("comment_num", 0)
    )
    if args.get("release_time") is None:
        movies = Movie.query.order_by(Movie.release_time.asc())
    elif args.get("release_time") == "1":
        movies = Movie.query.order_by(Movie.release_time.desc())
    else:
        movies = Movie.query.filter(
            and_(
                Movie.release_time >= datetime(year=int(args.get("release_time")), month=1, day=1),
                Movie.release_time < datetime(year=int(args.get("release_time")) + 1, month=1, day=1)
            )
        )
    if args.get("tag") and args.get("tag") != "0":
        movies = movies.filter_by(tag_id=args.get("tag"))

    if args.get("star_level") and int(args.get("star_level")) != 0:
        movies = movies.filter_by(star_level=args.get("star_level"))

    if args.get("play_num") and int(args.get("play_num")) != 0:
        movies = movies.order_by(
            Movie.play_num.desc() if args.get("play_num") == "1" else Movie.play_num.asc()
        )
    elif args.get("comment_num") and int(args.get("comment_num")) != 0:
        movies = movies.order_by(
            Movie.comment_num.desc() if args.get("comment_num") == "1" else Movie.comment_num.asc()
        )

    pagination = movies.paginate(page=page, per_page=1)
    tags = Tag.query.all()
    years = sorted(list(set([movie.release_time.year for movie in Movie.query.all()])), reverse=True)
    return render_template("home/index.html", tags=tags, years=years, args=args, pagination=pagination)


@home.route("/animation/")
def animation():
    previews = Preview.query.order_by(Preview.add_time.desc()).paginate(page=1, per_page=5)
    return render_template("home/animation.html", previews=previews)


@home.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_obj = User(
            name=form.name.data,
            password=generate_password_hash(form.password.data),
            email=form.email.data,
            phone=form.phone.data,
            uuid=uuid4().hex
        )
        db.session.add(user_obj)
        db.session.commit()
        flash("注册成功，请登录！", "succeed")
        return redirect(url_for("home.login"))
    return render_template("home/register.html", form=form)


@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        log = UserLog(ip=request.remote_addr, user_id=session.get("user_id"))
        db.session.add(log)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("home.index"))
    return render_template("home/login.html", form=form)


@home.route("/logout/")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for("home.login"))


@home.route("/user/", methods=["GET", "POST"])
@login_required_wraps("user", "home.login")
def user():
    form = UserDetailForm()
    user_obj = User.query.get(session.get("user_id"))
    if form.validate_on_submit():
        obj = User.query.filter_by(phone=form.phone.data).first()
        obj_2 = User.query.filter_by(email=form.email.data).first()
        if obj and obj is not user_obj:
            flash("此手机已存在！", "fail")
        elif obj_2 and obj_2 is not user_obj:
            flash("此邮箱已存在！", "fail")
        else:
            for k in form.data:
                if k == "photo":
                    filename = secure_filename(form.photo.data.filename)
                    if filename:
                        filename = handle_filename(filename)
                        user.photo = filename
                        form.photo.data.save(os.path.join(current_app.config["UPLOAD_DIR"], filename))
                elif k not in ["submit", "csrf_token"]:
                    setattr(user, k, getattr(form, k).data)
            db.session.add(user)
            db.session.commit()
            flash("修改资料", "succeed")
            return redirect(url_for("home.user"))

    for attr in ["email", "phone", "info"]:
        getattr(form, attr).data = getattr(user_obj, attr)
    return render_template("home/user.html", form=form, user=user_obj)


@home.route("/pwd/", methods=["GET", "POST"])
@login_required_wraps("user", "home.login")
def pwd():
    form = PasswordForm()
    if form.validate_on_submit():
        flash("修改密码成功，请重新登录！", "succeed")
        return redirect(url_for("home.logout"))
    return render_template("home/pwd.html", form=form)


@home.route("/comments/")
@home.route("/comments/<int:page>/")
@login_required_wraps("user", "home.login")
def comments(page=1):
    pagination = Comment.query.filter_by(
        user_id=session.get("user_id")
    ).order_by(
        Comment.add_time.desc()
    ).paginate(
        page=page, per_page=1
    )
    return render_template("home/comments.html", pagination=pagination)


@home.route("/login-log/")
@home.route("/login-log/<int:page>/")
@login_required_wraps("user", "home.login")
def login_log(page=1):
    pagination = UserLog.query.filter_by(user_id=session.get("user_id")).paginate(page=page, per_page=1)
    return render_template("home/login_log.html", pagination=pagination)


@home.route("/collect-add/<int:movie_id>/", methods=["POST"])
@login_required_wraps("user", "home.login")
def collect_add(movie_id):
    count = MovieCollect.query.filter_by(user_id=session.get("user_id"), movie_id=movie_id).count()
    if count:
        return jsonify(statuc="400", message="failed")
    col = MovieCollect(user_id=session.get("user_id"), movie_id=movie_id)
    db.session.add(col)
    db.session.commit()
    return jsonify(status="200", message="succeed")


@home.route("/movie-collect/")
@home.route("/movie-collect/<int:page>/")
@login_required_wraps("user", "home.login")
def movie_collect(page=1):
    pagination = MovieCollect.query.filter_by(
        user_id=session.get("user_id")
    ).order_by(
        MovieCollect.add_time.desc()
    ).paginate(page=page, per_page=1)
    return render_template("home/movie_collect.html", pagination=pagination)


@home.route("/search/")
@home.route("/search/<int:page>/")
def search(page=1):
    args = request.args.get("search")
    pagination = Movie.query.filter(Movie.title.ilike("%%%s%%" % args)).paginate(page=page, per_page=1)
    return render_template("home/search.html", pagination=pagination, args=args)


@home.route("/play/<int:movie_id>/", methods=["GET", "POST"])
def play(movie_id):
    form = CommentForm()
    movie = Movie.query.get_or_404(movie_id)
    page = int(request.args.get("page", 1))

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            movie_id=movie_id,
            user_id=session.get("user_id")
        )
        movie.comment_num += 1
        db.session.add_all([movie, comment])
        db.session.commit()
        flash("添加评论", "succeed")
        return redirect(url_for("home.play", movie_id=movie_id, page=page))

    pagination = Comment.query.filter(
        Comment.movie_id == movie_id
    ).order_by(
        Comment.add_time.desc()
    ).paginate(page=page, per_page=5)

    csrf_token = csrf.generate_csrf()

    return render_template("home/play.html", movie=movie, pagination=pagination, form=form, csrf_token=csrf_token)


@home.route("/video/<int:movie_id>/", methods=["GET", "POST"])
def video(movie_id):
    form = CommentForm()
    movie = Movie.query.get_or_404(movie_id)
    page = int(request.args.get("page", 1))

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            movie_id=movie_id,
            user_id=session.get("user_id")
        )
        movie.comment_num += 1
        db.session.add_all([movie, comment])
        db.session.commit()
        flash("添加评论", "succeed")
        return redirect(url_for("home.video", movie_id=movie_id, page=page))

    pagination = Comment.query.filter(
        Comment.movie_id == movie_id
    ).order_by(
        Comment.add_time.desc()
    ).paginate(page=page, per_page=5)

    csrf_token = csrf.generate_csrf()

    return render_template("home/video.html", movie=movie, pagination=pagination, form=form, csrf_token=csrf_token)


@home.route("/tm/", methods=["GET", "POST"])
def tm():
    import json
    if request.method == "GET":
        id = request.args.get("id")
        key = "movie" + str(id)
        if redis.llen(key):
            msgs = redis.lrange(key, 0, 2999)
            res = {
                "code": 1,
                "danmaku": [json.loads(v) for v in msgs]
            }
        else:
            res = {
                "code": 1,
                "danmuku": []
            }
        resp = json.dumps(res)
    if request.method == "POST":
        data = json.loads(request.get_data())
        msg = {
            "__v": 0,
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data["type"],
            "ip": request.remote_addr,
            "_id": datetime.now().strftime("%Y%m%d%H%M%S") + uuid4().hex,
            "player": [
                data["player"]
            ]
        }
        res = {
            "code": 1,
            "data": msg
        }
        resp = json.dumps(res)
        redis.lpush("movie" + str(data["player"]), json.dumps(msg))
    return Response(resp, mimetype="application/jsn")


@home.app_errorhandler(404)
def handle_404_error(error):
    return render_template("home/404.html", error=error), 404
