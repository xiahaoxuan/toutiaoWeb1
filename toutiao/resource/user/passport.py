from flask_restful import Resource
# from flask_limiter.util import get_remote_address
from flask import request, current_app, g
from flask_restful.reqparse import RequestParser
import random
import redis
from datetime import datetime, timedelta
from redis.exceptions import ConnectionError

# from celery_tasks.sms.tasks import send_verification_code
from . import constants

from utils import parser
from models import db
from models.user import User, UserProfile
from utils.jwt_util import generate_jwt
# from cache import user as cache_user
# from utils.limiter import limiter as lmt
# from utils.decorators import set_db_to_read, set_db_to_write


class SMSVerificationCodeResource(Resource):
    """
    短信验证码
    """
    error_message = 'Too many requests.'

    # decorators = [
    #     lmt.limit(constants.LIMIT_SMS_VERIFICATION_CODE_BY_MOBILE,
    #               key_func=lambda: request.view_args['mobile'],
    #               error_message=error_message),
    #     lmt.limit(constants.LIMIT_SMS_VERIFICATION_CODE_BY_IP,
    #               key_func=get_remote_address,
    #               error_message=error_message)
    # ]

    def get(self, mobile):
        code = '{:0>6d}'.format(random.randint(0, 999999))
        conn = current_app.redis_conn
        conn.setex('app:code:{}'.format(mobile), constants.SMS_VERIFICATION_CODE_EXPIRES, code)
        # send_verification_code.delay(mobile, code)
        return {'mobile': mobile, 'code': code}


class AuthorizationResource(Resource):
    """
    认证
    """
    def _generate_tokens(self, user_id, refresh=True):
        """
        生成token 和refresh_token
        :param user_id: 用户id
        :return: token, refresh_token
        """
        # 颁发JWT
        secret = current_app.config['JWT_SECRET']
        # 生成调用token， refresh_token
        expiry = datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])

        token = generate_jwt({'user_id': user_id}, expiry, secret)
        if refresh:
            exipry = datetime.utcnow() + timedelta(days=current_app.config['JWT_REFRESH_DAYS'])
            refresh_token = generate_jwt({'user_id': user_id, 'is_refresh': True}, exipry, secret)
        else:
            refresh_token = None

        return token, refresh_token

    def post(self):
        """
        登录创建token
        :return: token 和刷新token
        """
        json_parser = RequestParser()
        json_parser.add_argument('mobile', type=parser.mobile, required=True, location='json')
        json_parser.add_argument('code', type=parser.regex(r'^\d{6}$'), required=True, location='json')
        args = json_parser.parse_args()
        mobile = args.mobile
        code = args.code
        # 从redis中获取验证码
        key = 'app:code:{}'.format(mobile)
        try:
            real_code = current_app.redis_conn.get(key)
        except ConnectionError as e:
            current_app.logger.error(e)
        try:
            current_app.redis_conn.delete(key)
        except ConnectionError as e:
            current_app.logger.error(e)
        if not real_code or real_code.decode() != code:
            return {'message': 'Invalid code.'}, 400
        # 查询或保存用户
        user = User.query.filter_by(mobile=mobile).first()
        if user is None:
            # 用户不存在，注册用户
            # 采用雪花算法生成分布式id
            # 其他会用到雪花算法生成id的地方：文章id 评论id
            # 这三个id在代码中直接操作数据库使用，所以要全局唯一，使用雪花算法生成
            user_id = current_app.id_worker.get_id()
            user = User(id=user_id, mobile=mobile, name=mobile, last_login=datetime.now())
            db.session.add(user)
            profile = UserProfile(id=user.id)
            db.session.add(profile)
            db.session.commit()
        else:
            if user.status == User.STATUS.DISABLE:
                return {'message': 'Invalid user.'}, 403

        token, refresh_token = self._generate_tokens(user.id)

        return {'token': token, 'refresh_token': refresh_token}, 201

    def put(self):
        """
        刷新token
        :return:
        """
        user_id = g.user_id
        is_refresh = g.is_refresh
        if user_id is not None and is_refresh is True:
            token, refresh_token = self._generate_tokens(user_id, refresh=False)
            return {'token': token}
        else:
            return {'message': 'Invalid refresh token'}, 403







