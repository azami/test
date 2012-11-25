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


def encode_string(string):
    string = unicodedata.normalize('NFKC', string)
    return string.strip()


def exist_url(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return False
    return True
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
                results = results[start_num:start_num + SHOW_MAX]
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
        name = encode_string(request.form['name'])
        mail = encode_string(request.form['mail'])
        password = hashlib.md5(request.form['password']).hexdigest()
        site = encode_string(request.form['site'])
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


def update_tags(g, novel, new_tagdict, admin=False):
    '''
    new_tagdict = {tagname: {'edit': tag.edit,
                             'status': tag.status}
    '''
    if admin:
        old_taglist = novel.tag_list
    else:
        old_taglist = novel.active_tags
    old_tagdict = {}
    for tag in old_taglist:
        old_tagdict[tag.tag] = tag
    new_taglist = []
    banned_taglist = []
    disable_tagdict = {}
    if not admin:
        banned_taglist = [tag.tag for tag in novel.tag_list
                if not tag.status and not tag.edit]                              
        for tag in novel.tag_list:
            if not tag.status and tag.edit:
                disable_tagdict[tag.tag] = tag
    for tagstr in new_tagdict.keys():
        if tagstr in old_tagdict.keys():
            if admin:
                editable = new_tagdict[tagstr].get('edit', True)
                old_tagdict[tagstr].edit = editable
                old_tagdict[tagstr].status = new_tagdict[tagstr]['status']
            new_taglist.append(old_tagdict[tagstr])
        else:
            if not admin and tagstr in banned_taglist:
                continue
            if tagstr in disable_tagdict:
                tag = disable_tagdict[tagstr]
                tag.status = True
            else:
                tag = Tag(tag=tagstr, novel_id=novel.id)
            new_taglist.append(tag)
    delete_tags = set(old_taglist) -set(new_taglist)
    len(delete_tags)
    for tag in delete_tags:
        if admin:
            if not tag.status and not tag.edit:
                tag.edit = True
        tag.status = False
    g.db_session.add_all(list(delete_tags) + list(new_taglist))
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
        title = encode_string(request.form['title'])
        summary = encode_string(request.form['summary'])
        tags = {}
        new_taglist = set(re.sub(' \+', ' ',
                          encode_string(request.form['tags'])).split(' '))
        for tagstr in new_taglist:
            if tagstr:
                tags[tagstr] = {'status': True}
        if not novel:
            novel = g.db_session.query(Novel).filter(Novel.user_id == user_id).\
                filter(Novel.title == title).filter(Novel.status == False).first()
            if not novel:
                novel = Novel()
        novel.user_id = user_id
        novel.title = title
        novel.summary = summary
        novel.status = True
        g.db_session.add(novel)
        g.db_session.commit()
        update_tags(g, novel, tags, admin=True)
        return {'status': True, 'id': novel.id}
    except:
        message = u'登録に失敗しました'
        return_page = render_template('update_novel.htm', message=message,
                                      title=u'エラー', novel=request.form,
                                      conf=g.config)
        return {'status': False, 'page': return_page}


def delete_user(g, user_id, reason):
    try:
        user = g.db_session.query(User).filter(User.id == user_id).first()
        if not user:
            message = u'未知のエラーです'
            return internal_server_error(message)
        for novel in user.novel_list:
            for tag in novel.tag_list:
                tag.status = False
            novel.status = False
        user.mail += '+' + reason + str(datetime.date.today())
        user.status = False
        g.db_session.add(user)
        g.db_session.commit()
    except:
        pass


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
        user = g.db_session.query(User).filter(User.id == user_id).first()
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
