import random
import string

from flask import render_template
from flask import render_template_string

from flask_caching import make_template_fragment_key


def test_jinjaext_cache(app, cache):
    somevar = "".join([random.choice(string.ascii_letters) for x in range(6)])

    testkeys = [
        make_template_fragment_key("fragment1"),
        make_template_fragment_key("fragment1", vary_on=["key1"]),
        make_template_fragment_key("fragment1", vary_on=["key1", somevar]),
    ]
    delkey = make_template_fragment_key("fragment2")

    with app.test_request_context():
        #: Test if elements are cached
        render_template("test_template.html", somevar=somevar, timeout=60)
        for k in testkeys:
            assert cache.get(k) == somevar
        assert cache.get(delkey) == somevar

        #: Test timeout=del to delete key
        render_template("test_template.html", somevar=somevar, timeout="del")
        for k in testkeys:
            assert cache.get(k) == somevar
        assert cache.get(delkey) is None

        #: Test rendering templates from strings
        output = render_template_string(
            """{% cache 60, "fragment3" %}{{somevar}}{% endcache %}""",
            somevar=somevar,
        )
        assert cache.get(make_template_fragment_key("fragment3")) == somevar
        assert output == somevar

        #: Test backwards compatibility
        output = render_template_string(
            """{% cache 30 %}{{somevar}}{% endcache %}""", somevar=somevar
        )
        assert cache.get(make_template_fragment_key("None1")) == somevar
        assert output == somevar

        output = render_template_string(
            """{% cache 30, "fragment4", "fragment5"%}{{somevar}}{% endcache %}""",
            somevar=somevar,
        )
        k = make_template_fragment_key("fragment4", vary_on=["fragment5"])
        assert cache.get(k) == somevar
        assert output == somevar


def test_jinjaext_cache_non_string_keys(app, cache):
    assert make_template_fragment_key("fragment6", vary_on=[7, None]) == (
        make_template_fragment_key("fragment6", vary_on=["7", "None"])
    )

    with app.test_request_context():
        template = """{% cache 60, "fragment6", user_id %}{{ user_id }}{% endcache %}"""

        for user_id in (7, 8):
            output = render_template_string(template, user_id=user_id)
            k = make_template_fragment_key("fragment6", vary_on=[user_id])
            assert output == str(user_id)
            assert cache.get(k) == str(user_id)
