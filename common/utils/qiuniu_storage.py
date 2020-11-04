from qiniu import Auth, put_file, etag, put_data
from flask import current_app
import qiniu.config


def upload(file_data):
    # 需要填写你的 Access Key 和 Secret Key
    access_key = current_app.config['QINIU_ACCESS_KEY']
    secret_key = current_app.config['QINIU_SECRET_KEY']
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = current_app.config['QINIU_BUCKET_NAME']
    print('ak={}'.format(access_key))
    print('sk={}'.format(secret_key))
    print('bn={}'.format(bucket_name))
    # 上传后保存的文件名
    key = None
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    print('token={}'.format(token))
    # 要上传文件的本地路径
    # localfile = './sync/bbb.jpg'
    ret, info = put_data(token, key, file_data)
    print('ret={}'.format(ret))
    print('info={}'.format(info))
    return ret['key']
    # assert ret['key'] == key
    # assert ret['hash'] == etag(localfile)