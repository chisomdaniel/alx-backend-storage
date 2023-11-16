#!/usr/bin/env python3
'''implement an expiring web cache and tracker'''
import requests
from functools import wraps
from typing import Callable
import redis
from datetime import timedelta


def count_access(fn: Callable) -> Callable:
    '''count how many times a url was accessed'''
    @wraps(fn)
    def wrapper(url: str) -> str:
        '''wrapper function'''
        key = "count:{}".format(url)
        r = redis.Redis()
        count = r.get(key)
        if count is None:
            count = b'0'
        count = int(count.decode())
        r.setex(key, timedelta(seconds=10), value=count+1)
        return fn(url)
    return wrapper


@count_access
def get_page(url: str) -> str:
    '''get a page and return the content'''
    r = requests.get(url)
    return r.content
