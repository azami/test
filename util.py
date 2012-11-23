#-*- coding: utf-8 -*-
from db import User, Novel, Tag
from log_db import InLog, OutLog, UserLog, NovelLog
from config import SHOW_MAX
import urllib2
import hashlib
import unicodedata
import datetime
import re
import threading
import uuid
import base64
from flask import redirect, render_template, session

AGENT = 'tag_search_agent'
MOBAGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'


def generate_cookie():
    return base64.b64encode(uuid.uuid4().bytes)


def sanitize(string):
    string = unicodedata.normalize('NFKC', string)
    string = string.replace('<', '&lt;')
    string = string.replace('>', '&gt;')
    string = string.replace('&', '&amp;')
    string = string.replace('"', '&quot;')
    string = string.replace('\x27', '&#39;')
    return string.strip()


def sanitize_decode(string):
    string = string.replace('&lt;', '<')
    string = string.replace('&gt;', '>')
    string = string.replace('&amp;', '&')
    string = string.replace('&quot;', '"')
    string = string.replace('&#39;', '\x27')
    return string


def decode_user(user):
    decode_u = User()
    decode_u.name = sanitize_decode(user.name)
    decode_u.site = sanitize_decode(user.site)
    return user


def decode_novel(novel):
    decode_n = Novel()
    decode_n.title = sanitize_decode(novel.title)
    decode_n.summary = sanitize_decode(novel.summary)
    return decode_n


def exist_url(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return False
    agentreq = urllib2.Request(url)
    agentreq.add_header('User-Agent', AGENT)
    mobagentreq = urllib2.Request(url)
    mobagentreq.add_header('User-Agent', MOBAGENT)
    ### TODO
    try:
        for req in (agentreq, mobagentreq):
            t = threading.Thread(target=urllib2.urlopen(req))
        response = urllib2.urlopen(req)
        if response.code == 200:
            return True
        return True
    except Exception, e:
        return False


def search_result(page, results):
    num = len(results)
    start_num = page * SHOW_MAX
    try:
        if num > SHOW_MAX:
            if start_num + SHOW_MAX < SHOW_MAX:
                results = results[start_num:]
            else:
                results = results[start_result:start_result + SHOW_MAX]
        return results
    except:
        return 


def device(ua):
    if ua.find('au') >= 0 or ua.find('softbank') >= 0 or ua.find('docomo') >= 0:
        return 'mobile'
    if ua.find('iPhone') >= 0 or ua.find('iPod') >= 0 \
            or ua.find('Android') >= 0:
        return 'smartphone'
    return 'pc'


def check_form_user(request):
    if not request.form['name'] or not request.form['password']\
            or not request.form['site'] or not request.form['url']:
        return u'未入力の項目があります'
    if not request.form['password'] == request.form['password2']:
        return u'passwordが一致しません'
    url = request.form['url']
    if not exist_url(url):
        return u'URLにアクセスできません'


def update_user(request, g, user=None):
    message = check_form_user(request)
    if message:
        return_page = render_template('update_user.htm', message=message,
                                      user=request.form, conf=g.config)
        return {'status': False, 'page': return_page}
    try:
        name = sanitize(request.form['name'])
        mail = sanitize(request.form['mail'])
        password = hashlib.md5(request.form['password']).hexdigest()
        site = sanitize(request.form['site'])
        if not user:
            user = User()
        user.name = name
        user.mail = mail
        user.password = password
        user.site = site
        user.url = request.form['url'].encode('utf-8')
        g.db_session.add(user)
        g.db_session.commit()
        session['user'] = user.id
        return {'status': True}
    except:
        message = u'登録に失敗しました'
        return_page = render_template('error.htm', message=message, title=u'エラー',
                                      conf=g.config)
        return {'status': False, 'page': return_page}


def check_form_novel(request):
    if not request.form['title'] or not request.form['summary'].strip():
        return u'未入力の項目があります'
    if len(request.form['title']) > 255 or len(request.form['summary']) > 65534:
        return u'文字数が多すぎます'


def update_tags(novel, tags, g):
    update_tags = []
    novel_tags = [tag.tag for tag in novel.tag_list]
    for tag in novel.tag_list:
        if tag.tag in tags.keys():
            tag.status = True
            tag.edit = tags[tag.tag]
            update_tags.append(tag)
        else:
            if not tag.edit or session['user'] == novel.user_id:
                tag.status = False
                update_tags.append(tag)
    update_tags += [Tag(tag=tag, novel_id=novel.id) \
            for tag in tags.keys() if tag not in novel_tags]
    if update_tags:
        g.db_session.add_all(update_tags)
        g.db_session.commit()


def update_novel(request, g, novel=None):
    user_id = session['user']
    message = check_form_novel(request)
    if message:
        return_page = render_template('update_novel.htm', message=message,
                                      title=u'エラー', novel=request.form,
                                      conf=g.config)
        return {'status': False, 'page': return_page}

    try:
        title = sanitize(request.form['title'])
        summary = sanitize(request.form['summary'])
        tags = {}
        for tag in set(re.sub(' \+', ' ',
                              sanitize(request.form['tags'])).split(' ')):
            tags[tag] = True
        if not novel:
            novel = Novel()
        novel.user_id = user_id
        novel.title = title
        novel.summary = summary
        g.db_session.add(novel)
        g.db_session.commit()
        update_tags(novel, tags, g)
        return {'status': True, 'id': novel.id}
    except:
        message = u'登録に失敗しました'
        return_page = render_template('update_novel.htm', message=message,
                                      title=u'エラー', novel=request.form,
                                      conf=g.config)
        return {'status': False, 'page': return_page}


def logging_in(g, request, user_id=0):
    ua = request.headers['User-Agent']
    refer = request.headers.get('Referer')
    if refer and not refer.startswith(request.url_root):
        log = g.logdb_session.query(InLog).\
                filter(InLog.ua == ua).\
                filter(InLog.date == datetime.date.today()).\
                filter(InLog.ip == request.remote_addr).\
                filter(InLog.refer == refer).first()
        if not log:
            log = InLog()
            if 'user' in session:
                log.user_id = session['user']
            log.date = datetime.date.today()
            log.ua = ua
            log.ip = request.remote_addr
            log.refer = refer
            g.logdb_session.add(log)
            if user_id:
                user = g.db_session.query(User).filter(User.id == user_id).first()
                if not user:
                    return
                if user.id == user_id:
                    return
                if refer.startswith(user.url):
                    return
                user_log = g.logdb_session.query(UserLog).\
                        filter(UserLog.user_id == User.id).first()
                if not user_log:
                    user_log = UserLog(user_id=User.id)
                user_log.total_in += 1
                user_log.monthly_in += 1
                g.logdb_session.add(user_log)               
            g.logdb_session.commit()
                

def logging_out(g, request, url, novel_id):
    ua = request.headers['User-Agent']
    refer = request.headers.get('Referer')
    user_id = 0
    if 'user' in session:
        user_id = session['user']
        user = g.db_session(User).query.filter(User.id == user_id).one()
        if novel_id in [novel.id for novel in user.novel_list]:
            return
    outlog = g.logdb_session(OutLog).query.filter(OutLog.ua == ua).\
            filter(OutLog.ip == request.remote_addr).\
            filter(OutLog.date == datetime.datetime.today()).\
            filter(OutLog.novel_id == novel_id).first()
    if outlog:
        return
    outlog = OutLog()
    outlog.ua = ua
    outlog.ip = request.remote_addr
    outlog.date = datetime.datetime.today()
    outlog.novel_id = novel_id
    outlog.url = url
    if user_id:
        outlog.user_id = user_id
    novellog = session.query(NovelLog).filter(NovelLog.novel_id == novel_id)
    if not novellog:
        novellog = NovelLog(novel_id=novel_id)
    novellog.totai_out += 1
    novellog.monthly_out += 1
    g.logdb_session.add_all([outlog, novellog])
    g.logdb_session.commit()
