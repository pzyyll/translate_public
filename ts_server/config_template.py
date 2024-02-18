# -*- coding:utf-8 -*-
# @Date: "2024-02-16"
# @Description: flask app config

FLASK_ADMIN_SWATCH = "cerulean"
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = '123456'
RECAPTCHA_PUBLIC_KEY = "your_recaptcha_public_key"
RECAPTCHA_PRIVATE_KEY = "your_recaptcha_private_key"
SESSION_TYPE = 'filesystem'
TESTING = True