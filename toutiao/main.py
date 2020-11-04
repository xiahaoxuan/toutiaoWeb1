import os
import sys
import redis

from flask import jsonify
from . import create_app
from settings.default import DefaultConfig
from models.user import User

from utils.qiuniu_storage import upload

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))


app = create_app(DefaultConfig, enable_config_file=True)
# redis_con = redis.Connection(host='localhost', port='6379', db=0)


@app.route('/')
def route_map():
    """
    主视图，返回所有视图
    :return:
    """
    # ret = User.query.all()
    # print(ret)
    # 普通连接
    # conn = redis.Redis(host="localhost", port=6379,)
    # conn.set("x1", "hello", ex=50)  # ex代表seconds，px代表ms
    # val = conn.get("x1")
    # print(val)
    # 七牛云
    # f = open('/home/user/1.JPG', 'rb')
    # file_data = f.read()
    # ret = upload(file_data)
    # return ret
    rules_iterator = app.url_map.iter_rules()
    return jsonify({rule.endpoint: rule.rule for rule in rules_iterator if rule.endpoint not in ('route_map', 'static')})
