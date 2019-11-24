import random
from datetime import datetime

from flask import Flask, jsonify, render_template_string

from flask_caching import Cache

app = Flask(__name__)
app.config.from_pyfile("hello.cfg")
cache = Cache(app)


#: This is an example of a cached view
@app.route("/api/now")
@cache.cached(50)
def current_time():
    return str(datetime.now())


#: This is an example of a cached function
@cache.cached(key_prefix="binary")
def random_binary():
    return [random.randrange(0, 2) for i in range(500)]


@app.route("/api/get/binary")
def get_binary():
    return jsonify({"data": random_binary()})


#: This is an example of a memoized function
@cache.memoize(60)
def _add(a, b):
    return a + b + random.randrange(0, 1000)


@cache.memoize(60)
def _sub(a, b):
    return a - b - random.randrange(0, 1000)


@app.route("/api/add/<int:a>/<int:b>")
def add(a, b):
    return str(_add(a, b))


@app.route("/api/sub/<int:a>/<int:b>")
def sub(a, b):
    return str(_sub(a, b))


@app.route("/api/cache/delete")
def delete_cache():
    cache.delete_memoized("_add", "_sub")
    return "OK"


@app.route("/html")
@app.route("/html/<foo>")
def html(foo=None):
    if foo is not None:
        cache.set("foo", foo)
    return render_template_string(
        "<html><body>foo cache: {{foo}}</body></html>", foo=cache.get("foo")
    )


@app.route("/template")
def template():
    dt = str(datetime.now())
    return render_template_string(
        """<html><body>foo cache:
            {% cache 60, "random" %}
                {{ range(1, 42) | random }}
            {% endcache %}
        </body></html>"""
    )


if __name__ == "__main__":
    app.run()
