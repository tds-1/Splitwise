from functools import wraps

from splitwise_api.exceptions import AuthenticationError
from splitwise_api.utils import SplitwiseUtils


def is_authenticated():
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):

            request = args[0].request  # args[0] is the instance of view class
            access_token = request.headers.get("access_token")

            if not access_token:
                raise AuthenticationError
            splitwise_obj = SplitwiseUtils(access_token)
            try:
                user_info = splitwise_obj.get_current_user()
            except Exception as e:
                raise AuthenticationError

            request.user = user_info
            request.splitwise_obj = splitwise_obj
            args[0].request = request

            return f(*args, **kwargs)

        return wrapped_f

    return wrap
