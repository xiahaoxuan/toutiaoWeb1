class DefaultConfig(object):
    """
    Flask默认配置
    """
    ERROR_404_HELP = False

    # 日志
    LOGGING_LEVEL = 'DEBUG'
    LOGGING_FILE_DIR = '/home/user/logs'
    LOGGING_FILE_MAX_BYTES = 300 * 1024 * 1024
    LOGGING_FILE_BACKUP = 10

    # flask-sqlalchemy使用的参数
    SQLALCHEMY_DATABASE_URI = 'mysql://root:54Haoxuan!@127.0.0.1:3306/toutiao'  # 数据库
    # SQLALCHEMY_BINDS = {
    #     'bj-m1': 'mysql://root:mysql@127.0.0.1:3306/toutiao',
    #     'bj-s1': 'mysql://root:mysql@127.0.0.1:8306/toutiao',
    #     'masters': ['bj-m1'],
    #     'slaves': ['bj-s1'],
    #     'default': 'bj-m1'
    # }

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 追踪数据的修改信号
    SQLALCHEMY_ECHO = True

    # JWT
    JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'
    JWT_EXPIRY_HOURS = 2
    JWT_REFRESH_DAYS = 14

    # Snowflake ID Worker 参数
    DATACENTER_ID = 0
    WORKER_ID = 0
    SEQUENCE = 0

