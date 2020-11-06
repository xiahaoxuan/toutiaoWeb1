from flask import current_app

from redis.exceptions import ConnectionError


class CountStorageBase(object):
    """
    统计数量存储的父类
    """
    key = ''

    @classmethod
    def get(cls, user_id):
        # 查询redis记录
        # 如果redis存在记录
        # 返回
        # 如果redis不存在记录，则返回0，表示用户没有发表过文章
        try:
            count = current_app.redis_conn.zscore(cls.key, user_id)
        except ConnectionError as e:
            current_app.logger.error(e)
            # count = current_app.redis_conn.zscore(cls.key, user_id)

        if count is None:
            return 0
        else:
            return int(count)

    @classmethod
    def increment(cls, user_id, incr_num=1):
        try:
            current_app.redis_conn.zincrby(cls.key, user_id, incr_num)
        except ConnectionError as e:
            current_app.logger.error(e)
            raise e


class UserArticleCountStorage(CountStorageBase):
    """
    用户文章数量redis存储工具类
    """
    key = 'count:user:arts'


class UserFollowingCountStorage(CountStorageBase):
    """
    用户关注数量
    """
    key = 'count:user:followings'