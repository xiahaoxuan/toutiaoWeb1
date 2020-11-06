import random


class CacheTTLBase(object):
    """
    缓存数据有效期的父类
    """
    TTL = 2 * 60 * 60  # 有效期的基准值
    MAX_DELTA = 10 * 60  # 有效期的最大随机偏差值

    @classmethod
    def get_value(cls):
        return cls.TTL + random.randrange(0, cls.MAX_DELTA)


# # 用户基本信息的有效期, 秒
# USER_CACHE_DATA_TTL = 2 * 60 * 60
#
# def get_value():
#     return USER_CACHE_DATA_TTL + random.randrange(0, 600)

class UserCacheDataTTL(CacheTTLBase):
    """
    用户基本信息的有效期
    """
    pass


class UserNotExistCacheTTL(CacheTTLBase):
    """
    用户不存在缓存的有效期
    """
    TTL = 5 * 60
    MAX_DELTA = 60


class ArticleCacheDataTTL(CacheTTLBase):
    """
    文章基本信息的有效期
    """
    TTL = 60 * 60
    MAX_DELTA = 5 * 60