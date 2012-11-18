# -*- coding: utf-8 -*-

from flask import Flask, request, g, render_template, url_for, session, redirect
from config import Config
from sqlalchemy import func
from db import User, Novel, Tag
import util
from urlparse import urljoin
import hashlib

app = Flask(__name__)
app.config.from_object(Config)


def require_login(func):
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if request.url.startswith('http://') and not app.debug:
            return redirect(url.replace('http://', 'https://', 1))
        if not 'user' in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


@app.route('/')
def index():
    return render_template('index.htm', config=g.config)


@app.route('/user/<int:user_id>')
@require_login
def user_index(user_id):
    user = g.db_session.query(User).filter(User.id == user_id).first()
    if not user:
        message = u'未知のエラーです'
        return render_template('error.htm', message=message)
    return render_template('profile.htm', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if not app.debug:
            g.config['root'] = request.url_root.replace('http://',
                                                        'https://', 1)
        return render_template('login.htm', conf=g.config)
    user = g.db_session.query(User).filter(User.mail ==\
                                           request.form['mail']).first()
    if user:
        if user.password == hashlib.md5(request.form['password']).hexdigest():
            session['user'] = user.id
            g.user = user
            print url_for('user_index', user_id=user.id)
            return redirect(url_for('user_index', user_id=user.id))
    g.config['message'] = u'メールアドレスまたはパスワードが違います'
    return render_template('error.htm', conf=g.config)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/signup')
def signup():
    path = urljoin(request.url_root, url_for('register'))
    if not app.debug:
        path = request.url_root.replace('http://', 'https://', 1)
    return render_template('update_user.htm', path=path, user=None)


@app.route('/register', methods=['POST'])
def register():
    return util.update_user(request, g)


@app.route('/user/<int:user_id>/edit_profile', methods=['GET', 'POST'])
@require_login
def edit_profile(user_id):
    if request.method == 'GET':
        user = g.db_session.query(User).filter(User.id == user_id).first()
        if not user:
            message = u'未知のエラーです'
            return render_template('error.htm', message=message)
        return render_template('update_user.htm', path=request.base_url,
                               user=user)
    return util.update_user(request, g, user_id)


@require_login
@app.route('/user/<int:user_id>/add_novel', methods=['GET', 'POST'])
def add_novel(user_id):
    if request.method == 'GET':
        return render_template('add_novel.htm', conf=None)

#    try:
    user_id = user_id
    if not request.form['title'] or not request.form['summary']:
        g.config['message'] = u'未入力の項目があります'
        return render_template('add_novel.htm', conf=g.config)

    title = util.sanitize(request.form['title'])
    summary = util.sanitize(request.form['summary'])
    novel = Novel(user_id=user_id,
                   title=title,
                   summary=summary)
    g.db_session.add(novel)
    g.db_session.commit()
    print g.db_session.query(Novel).all()
    return 'touroku'
    return render_template('novel.htm', app.config)
#    except:
#        return 'error'
#        return render_template('error.htm', app.config)
