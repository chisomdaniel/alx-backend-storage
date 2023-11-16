#!/usr/bin/env python3
'''redis exercise'''
import redis
from typing import Any, Callable, Union
import uuid
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''count how many times a function is called'''
    @wraps(method)
    def wrapper(self, data: Union[str, bytes, int, float]) -> str:
        '''wrapper function'''
        self._redis.incr(method.__qualname__)
        return method(self, data)
    return wrapper


def call_history(method: Callable) -> Callable:
    '''log input parameter and output value from function'''
    @wraps(method)
    def wrapper(self, *args: Union[str, bytes, int, float]) -> str:
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"
        self._redis.rpush(input_key, str(args))
        output = method(self, *args)
        self._redis.rpush(output_key, output)
        return output
    return wrapper


class Cache:
    '''main redis class'''

    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''store a data to db'''
        key = str(uuid.uuid4())
        self._redis.set(key, data)

        return key

    def get(self, key: str, fn: Callable = None) -> str:
        '''get data from db'''
        if fn is None:
            return self._redis.get(key)

        data = self._redis.get(key)
        if data is None:
            return None

        return fn(data)

    def get_str(self, bstr: bytes) -> str:
        '''convert the output to string'''
        return bstr.decode()

    def get_int(self, bstr: bytes) -> int:
        '''conver the output to int'''
        return int(bstr.decode())


def replay(method: Callable) -> None:
    '''display the history of calls of a particular function'''
    if method is None:
        return

    r = redis.Redis()
    count = r.get(method.__qualname__)
    inputs = r.lrange(method.__qualname__ + ":inputs", 0, -1)
    outputs = r.lrange(method.__qualname__ + ":outputs", 0, -1)

    print("{} was called {} times:".format(method.__qualname__,
                                           (count).decode()))

    for i, j in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(method.__qualname__,
                                     i.decode(), j.decode()))
