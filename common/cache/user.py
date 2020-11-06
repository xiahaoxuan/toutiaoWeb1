import json
import random

from flask import current_app
from sqlalchemy.orm import load_only
from sqlalchemy.exc import DatabaseError
from redis.exceptions import RedisError


from models.user import User
from . import constants


class UserProfileCache(object):
    """
    用户基本信息缓存工具
    """
    def __init__(self, user_id):
        self.key = 'user:{}:profile'.format(user_id)
        self.user_id = user_id

    def save(self):
        """
        保存缓存记录
        :return:
        """
        r = current_app.redis_conn
        try:
            user = User.query.options(load_only(
                User.mobile,
                User.name,
                User.profile_photo,
                User.introduction,
                User.certificate
            )).filter_by(id=self.user_id).first()
        except DatabaseError as e:
            current_app.logger.error(e)
            # 对于这个数据库异常，我们自己封装的get方法无法为调用者做决定，决定返回什么值，所以抛出异常给调用者，由调用者决定
            raise e

        # 在django中 查询单一对象，而数据库不存在，抛出异常  User.DoesNotExists
        # 在sqlalchemy中，查询单一对象，数据库不存在，不抛出异常，只返回None
        if user is None:
            # 数据库不存在
            try:
                r.setex(self.key, constants.UserNotExistCacheTTL.get_value(), -1)
            except RedisError as e:
                current_app.logger.error(e)

            return None
        else:
            user_dict = {
                'mobile': user.mobile,
                'name': user.name,
                'photo': user.profile_photo,
                'intro': user.introduction,
                'certi': user.certificate
            }
            try:
                r.setex(self.key, constants.UserCacheDataTTL.get_value(), json.dumps(user_dict))
            except RedisError as e:
                current_app.logger.error(e)

            return user_dict

    def get(self):
        """
        获取返回数据
        :return:
        """
        r = current_app.redis_conn
        try:
            ret = r.get(self.key)
        except RedisError as e:
            # 记录日志
            current_app.logger.error(e)
            # 在redis出现异常的时候，为了保证我们封装的get方法还能有返回值，可以进入数据库查询的部分
            ret = None

        if ret is not None:
            # 表示redis中有数据
            if ret == b'-1':
                return None
            else:
                user_dict = json.loads(ret)
                return user_dict
        else:
            return self.save()


    def clear(self):
        """
        清除缓存数据
        :return:
        """
        try:
            current_app.redis_conn.delete(self.key)
        except RedisError as e:
            current_app.logger.error(e)

    def determine_user_exists(self):
        """
        判断缓存是否存在
        :return:
        """
        # 查询redis
        r = current_app.redis_conn
        try:
            ret = r.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            ret = None

        # 如果缓存记录存在
        if ret is not None:
            if ret == b'-1':
                # 如果缓存记录为-1 ，表示用户不存在
                return False
            else:
                # 如果缓存记录不为-1， 表示用户存在
                return True

        # 如果缓存记录不存在，查询数据库
        else:
            cache_data = self.save()
            if cache_data is not None:
                return True
            else:
                return False