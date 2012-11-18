#-*- coding: utf-8 -*-
from db import User, Novel, Tag
import urllib2
import hashlib
from flask import render_template, session

AGENT = 'tag_search_agent'


def sanitize(string):
    string = string.replace('<', '&lt;')
    string = string.replace('>', '&gt;')
    string = string.replace('&', '&amp;')
    string = string.replace('"', '&quot;')
    string = string.replace('\x27', '&#39;')
    return string


def exist_url(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        print url.startswith('http://')
        print url
        return False
    req = urllib2.Request(url)
    req.add_header('User-Agent', AGENT)
    try:
        response = urllib2.urlopen(req)
        if response.code == 200:
            return True
        return False
    except:
        return False

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


def update_user(request, g, user_id=0):
    message = check_form_user(request)
    if message:
        return render_template('update_user.htm', message=message,
                               user=request.form)
    try:
        name = sanitize(request.form['name'])
        mail = sanitize(request.form['mail'])
        password = hashlib.md5(request.form['password']).hexdigest()
        site = sanitize(request.form['site'])
        if user_id:
            user = g.db_session.query(User).filter(User.id == user_id).one()
        else:
            user = User()
        user.name = name
        user.mail = mail
        user.password = password
        user.site = site
        user.url = request.form['url']
        g.db_session.add(user)
        g.db_session.commit()
        session['user'] = user.id
        return render_template('profile.htm', user=user)
    except:
        message = u'登録に失敗しました'
        return render_template('error.htm', message=message)
