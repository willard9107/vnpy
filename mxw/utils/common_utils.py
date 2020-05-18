from mxw.utils.common_import import *

import redis
import redis_lock

redis_conn = redis.StrictRedis(host='nas.willard.love', port=32778)


def error_log_with_ding_talk(msg: str):
    print(msg, file=sys.stderr)
    dingtalk_utils.send_message(msg)
