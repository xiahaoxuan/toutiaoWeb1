from flask import Flask
import redis


def create_flask_app(config, enable_config_file=False):
    """
    创建Flask应用
    :param config: 配置信息对象
    :param enable_config_file: 是否允许运行环境中的配置文件覆盖已加载的配置信息
    :return: Flask应用
    """
    app = Flask(__name__)
    app.config.from_object(config)
    if enable_config_file:
        from utils import constants
        app.config.from_envvar(constants.GLOBAL_SETTING_ENV_NAME, silent=True)

    return app


def create_app(config, enable_config_file=False):
    """
    创建应用
    :param config: 配置信息对象
    :param enable_config_file: 是否允许运行环境中的配置文件覆盖已加载的配置信息
    :return: 应用
    """
    app = create_flask_app(config, enable_config_file)
    # 创建Snowflake ID worker
    from utils.snowflake.id_worker import IdWorker
    app.id_worker = IdWorker(app.config['DATACENTER_ID'],
                             app.config['WORKER_ID'],
                             app.config['SEQUENCE'])
    # 限流器
    from utils.limiter import limiter as lmt
    lmt.init_app(app)
    # 配置日志
    from utils.logging import create_logger
    create_logger(app)
    # 注册url转换器
    from utils.converters import register_converters
    register_converters(app)
    # 连接redis
    conn = redis.Redis(host="localhost", port=6379)
    app.redis_conn = conn
    # MySQL数据库连接初始化
    from models import db

    db.init_app(app)

    # 添加请求钩子
    from utils.middlewares import jwt_authentication
    app.before_request(jwt_authentication)

    # 注册用户模块蓝图
    from .resource.user import user_bp
    app.register_blueprint(user_bp)

    return app


