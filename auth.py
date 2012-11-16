#-*- coding: utf-8 -*-
import oauth2
import config
import json
from flask import Flask, request, redirect


app = Flask(__name__)
app.debug = True
app.secret = 'test'


def parse_token(token):
    print token
    return dict([x.split('=') for x in token.split('&')])



def auth_twitter(conf):
    consumer = oauth2.Consumer(key=conf.TWITTER_CONSUMER_KEY,
                               secret=conf.TWITTER_CONSUMER_SECRET)
    client = oauth2.Client(consumer)
    response, token = client.request(conf.TWITTER_REQUEST_URL, 'GET')
    if response.status == 200:
        access_token = parse_token(token)
        return '%s?oauth_token=%s' % (conf.TWITTER_AUTH_URL,
                                      access_token['oauth_token'])
    return 'error'

@app.route('/')
def auth():
    return redirect(auth_twitter(config.Config))



if __name__ == '__main__':
    app.run(port=8080)
