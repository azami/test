#-*- coding: utf-8 -*-
#from oauth2client.client import OAuth2WebServerFlow
#from config import Config
from flask import Flask, request, redirect, render_template, jsonify


app = Flask(__name__)


@app.route('/')
def auth():
    return 'test'
    return render_template('base.htm', dev_key=Config.dev_key,
                           callback=Config.host + '/callback')


@app.route('/callback', methods=['GET', 'POST'])
def callback():
    return request.args


@app.route('/userstatus', methods=['POST'])
def user_status():
    return jsonify(registered=True)


@app.route('/login', methods=['POST'])
def login():
    print request.form
    return jsonify(status='OK')


if __name__ == '__main__':
    app.run()
