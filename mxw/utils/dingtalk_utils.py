import time
import hmac
import hashlib
import base64
import urllib.parse
import requests


def send_message(message: str, at_users=None, is_at_all=False):
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=f77f0641a38f62adb54649570b534165b42db34bb746409a92c2c79c7d12c351'

    timestamp = str(round(time.time() * 1000))
    secret = 'SECb6d442fc2afcee9b44e51d704d618804b9e5291cc363bb534569a54af07b0573'
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url_path = '{}&timestamp={}&sign={}'.format(webhook, timestamp, sign)
    payload = {'msgtype': 'text', 'text': {'content': message}}

    if at_users or is_at_all:
        payload['at'] = {}

    if is_at_all:
        payload['at']['isAtAll'] = True

    if at_users:
        payload['at']['atMobiles'] = at_users

    requests.post(url_path, json=payload)


if __name__ == '__main__':
    # send_message('这是一条测试 @18614069492 @13051059554 消息', ['13051059554'])
    send_message('这是一条测试at all @18614069492 消息', is_at_all=True)
