import functools
import logging
import re
import time

logger = logging.getLogger('dinero')


def args_kwargs_to_call(args, kwargs):
    """
    Turns args (a list) and kwargs (a dict) into a string that looks like it could be used to call a function with positional and keyword arguments.

    >>> args_kwargs_to_call([1], {})
    '1'
    >>> args_kwargs_to_call([1,2], {})
    '1, 2'
    >>> args_kwargs_to_call([1], {'foo':'bar'})
    "1, foo='bar'"

    """
    ret = []
    for arg in args:
        if ret:
            ret.append(", ")
        ret.append(repr(arg))
    for k, v in kwargs.iteritems():
        if ret:
            ret.append(", ")
        ret.append("%s=%r" % (k, v))
    return ''.join(ret)


def log(fn):
    """
    Wraps fn in logging calls
    """
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        start_time = time.time()

        def logit(exception=None):
            if exception:
                exception_message = ' and raised %r' % exception
            else:
                exception_message = ''

            end_time = time.time()
            message = '%s(%s) took %s seconds%s' % (
                fn.__name__,
                args_kwargs_to_call(args, kwargs),
                end_time - start_time,
                exception_message)
            # remove any credit card numbers
            message = re.sub(r"\b([0-9])[0-9- ]{9,16}([0-9]{4})\b", r'\1XXXXXXXXX\2', message)
            logger.info(message)

        try:
            value = fn(*args, **kwargs)
            logit()
            return value
        except Exception as e:
            logit(e)
            raise

    return inner
