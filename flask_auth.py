#-*- coding: utf-8 -*-
from oauth2client.client import OAuth2WebServerFlow
from config import Config
from flask import Flask, request, redirect, render_template


app = Flask(__name__)


@app.route('/')
def auth():
    print Config.dev_key
    return render_template('base.htm', dev_key=Config.dev_key,
                           callback=Config.host + '/callback')


@app.route('/callback')
def callback():
    return request.args

if __name__ == '__main__':
    app.run()
