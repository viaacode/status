from functools import wraps, partial
from flask import request, render_template


def cached(timeout=5 * 60, key='view/%s', cache=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            cache_key = key % request.path
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated
    return decorator


def cacher(cache):
    return partial(cached, cache=cache)


def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated
    return decorator
