#-*- coding: utf-8 -*-
from oauth2client.client import OAuth2WebServerFlow
import config
from flask import Flask, request, redirect


app = Flask(__name__)
app.debug = True
app.secret = 'test'


def parse_token(token):
    print token
    return dict([x.split('=') for x in token.split('&')])



def auth_google(conf):
    print 'hoge'
    flow = OAuth2WebServerFlow(client_id=conf.CLIENT_ID,
                               client_secret=conf.CLIENT_SECRET,
                               scope=conf.AUTH_SCOPE,
                               redirect_uri=conf.HOST + 'auth')
    auth_uri = flow.step1_get_authorize_url()
    print auth_uri
    return auth_uri


@app.route('/auth')
def auth_return():
    credentials = flow.step2_exchange(code)
    print credintials
    return 'test'


@app.route('/')
def auth():
    return redirect(auth_google(config.Config))


if __name__ == '__main__':
    app.run(port=8080)
