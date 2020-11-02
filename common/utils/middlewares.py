from flask import request, g
from utils.jwt_util import verify_jwt


def jwt_authentication():
    g.user_id = None
    g.is_refresh = False
    token = request.headers.get('Authorization')
    if token is not None and token.startswith('Bearer '):
        token = token[7:]
        # 验证token
        payload = verify_jwt(token)
        if payload is not None:
            # 保存到g对象中
            g.user_id = payload.get('user_id')
            g.is_refresh = payload.get('is_refresh', False)