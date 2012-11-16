#-*- coding: utf-8 -*-
from oauth2client.client import OAuth2WebServerFlow
import config as conf
from flask import Flask, request, redirect


app = Flask(__name__)
app.secret = 'test'

flow = OAuth2WebServerFlow(client_id=conf.Config.CLIENT_ID,
                           client_secret=conf.Config.CLIENT_SECRET,
                           scope=conf.Config.AUTH_SCOPE,
                           redirect_uri=conf.Config.HOST + 'auth')


def auth_google():
    print 'hoge'
    flow = OAuth2WebServerFlow(client_id=conf.Config.CLIENT_ID,
                               client_secret=conf.Config.CLIENT_SECRET,
                               scope=conf.Config.AUTH_SCOPE,
                               redirect_uri=conf.Config.HOST + 'auth')
    auth_uri = flow.step1_get_authorize_url()
    print auth_uri
    return auth_uri


@app.route('/auth')
def auth_return():
    credentials = flow.step2_exchange(request.args.get('code', ''))
    print credintials
    return 'test'


@app.route('/')
def auth():
    return redirect(auth_google())


if __name__ == '__main__':
    app.run()
