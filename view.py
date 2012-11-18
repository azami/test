# -*- coding: utf-8 -*-

from flask import Flask, request, g, render_template, url_for, session, redirect
from config import Config, ROBOTS
from db import User, Novel, Tag
import util
from urlparse import urljoin
import hashlib
import urllib2

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


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.htm', message=error), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.htm', message=error), 500


@app.route('/robots.txt')
def robots():
    if ROBOTS:
        return ROBOTS
    return page_not_found('')


@app.route('/')
def index():
    tag_list = [x[0] for x in \
                      g.db_session.query(Tag.tag).filter(Tag.status == True).all()]
    sorted_tag = sorted(set(tag_list),
                        reverse=True, key=lambda x: tag_list.count(x))
    if len(tag_list) > 200:
        sorted_tag = sorted_tag[:200]
    tags={}
    print len(tag_list)
    for tag in sorted_tag:
        print tag_list.count(tag)
        print int(len(tag_list) // tag_list.count(tag))
        tags[tag]= {'size': int(len(tag_list) // tag_list.count(tag)),
                    'num': tag_list.count(tag)}
    return render_template('index.htm', tags=tags)


@app.route('/tag/<tag>')
@app.route('/tag/<tag>/<int:page>')
def tag_search(tag, page=0):
    tags = g.db_session.query(Tag).filter(Tag.tag == tag).filter(Tag.status\
                                                                 == True).all()
    tags = util.search_result(page, tags)
    if not tags:
        return page_not_found(u'検索結果がないです')
    novels = [tag.novel for tag in tags if tag.novel.status]
    novels = sorted(novels, key=lambda x: x.id)
    return render_template('search.htm', novels=novels)


@app.route('/search')
@app.route('/search/<int:page>')
def search(page=0):
    novels = []
    words = util.sanitize(request.args['words']).split()
    user_query = g.db_session.query(User).filter(User.status == True)
    novel_query = g.db_session.query(Novel).filter(Novel.status == True)
    tag_query = g.db_session.query(Tag).filter(Tag.status == True)
    for word in words:
        user_query = user_query.filter(User.name.like(word))
        novel_query = novel_query.filter(Novel.title.like(word))
        novel_query = novel_query.filter(Novel.summary.like(word))
        tag_query = tag_query.filter(Tag.tag == word)

    users = user_query.all()
    for user in users:
        novels += [novel for novel in user.novel_list if novel.status]
    novels += novel_query.all()
    tags = tag_query.all()
    novels += [tag.novel for tag in tags if tag.novel.status]
    novels = sorted(util.search_result(page, set(novels)), key=lambda x: x.id)
    if not novels:
        return page_not_found(u'検索結果がないです')
    return render_template('search.htm', novels=novels)
    

@app.route('/user')
@require_login
def user_index():
    user = g.db_session.query(User).filter(User.id == session['user']).first()
    if not user:
        message = u'未知のエラーです'
        return render_template('error.htm', message=message)
    #print url_for('link_to_site', hoge=urllib2.quote(user.url))
    print url_for('link_to_site', link='test')
    return render_template('profile.htm',
                           url=url_for('link_to_site',
                                       link=urllib2.quote(user.url)),
                           user=user, novels=user.novel_list)


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
            return redirect(url_for('user_index'))
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
    result = util.update_user(request, g)
    if not result['status']:
        return result['page']
    return redirect(url_for('user_index'))


@app.route('/user/edit_profile', methods=['GET', 'POST'])
@require_login
def edit_profile():
    user = g.db_session.query(User).filter(User.id == session['user']).first()
    if not user:
        message = u'未知のエラーです'
        return internal_server_error(message)
    if request.method == 'GET':
        decode_user = util.decode_user(user)
        return render_template('update_user.htm', path=request.base_url,
                               user=decode_user)
    result = util.update_user(request, g, user)
    if not result['status']:
        return result['page']
    return redirect(url_for('user_index'))


@app.route('/novel/<int:novel_id>')
def novelinfo(novel_id):
    novel = g.db_session.query(Novel).filter(Novel.id == novel_id).one()
    return render_template('novel.htm', novel=novel)


@require_login
@app.route('/user/add_novel', methods=['GET', 'POST'])
def add_novel():
    if request.method == 'GET':
        return render_template('update_novel.htm', title=u'小説登録',
                               novel=None)
    (result, return_code) = util.update_novel(request, g)
    if not result:
        return return_code
    return redirect(url_for('novelinfo', novel_id=return_code))


@app.route('/user/edit_novel/<int:novel_id>', methods=['GET', 'POST'])
@require_login
def edit_novel(novel_id):
    novel = g.db_session.query(Novel).filter(Novel.user_id == session['user'],
                                             Novel.id == novel_id).first()
    if not novel:
        message = u'未知のエラーです'
        return internal_server_error(message)

    tags = [tag.tag for tag in novel.tag_list if tag.status]
    if request.method == 'GET':
        decode_novel = util.decode_novel(novel)
        decode_tags = [util.sanitize_decode(tag) for tag in tags]
        return render_template('update_novel.htm', title=u'小説情報編集',
                               novel=decode_novel, tags=' '.join(decode_tags))
    result = util.update_novel(request, g, novel)
    if not result['status']:
        return result['page']
    return redirect(url_for('novelinfo', novel_id=result['id']))



@app.route('/user/quit')
@require_login
def quit():
    user = g.db_session.query(User).filter(User.id == session['user']).first()
    if not user:
        message = u'未知のエラーです'
        return internal_server_error(message)
    for novel in user.novel_list:
        for tag in novel.tag_list:
            tag.status = False
        novel.status = False
    user.status = False
    g.db_session.add(user)
    g.db_session.commit()
    return redirect(url_for('logout'))


@app.route('/user/delete_novel/<int:novel_id>')
@require_login
def delete_novel(novel_id):
    novel = g.db_session.query(Novel).filter(Novel.user_id == session['user'],
                                             Novel.id == novel_id).first()
    if not novel:
        message = u'未知のエラーです'
        return internal_server_error(message)
    for tag in novel.tag_list:
        tag.status = False
    novel.status = False
    g.db_session.add(novel)
    g.db_session.commit()
    return redirect(url_for('user_index'))


@app.route('/link')
def link_to_site():
    link = urllib2.unquote(request.args['link']).encode('utf-8')
    return redirect(link)
