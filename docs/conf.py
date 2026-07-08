from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

project = "Flask-Caching"
copyright = "2016, Thadeus Burgess, Peter Justin"
author = "Thadeus Burgess, Peter Justin"
release, version = get_version("Flask-Caching")

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "pallets_sphinx_themes",
    "sphinxcontrib.log_cabinet",
]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_preserve_defaults = True
extlinks = {
    "issue": ("https://github.com/pallets-eco/flask-caching/issues/%s", "#%s"),
    "pr": ("https://github.com/pallets-eco/flask-caching/pull/%s", "#%s"),
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "flask": ("https://flask.palletsprojects.com/", None),
}

issues_github_path = "pallets-eco/flask-caching"


html_theme = "flask"
html_context = {
    "project_links": [
        ProjectLink("PyPI Releases", "https://pypi.python.org/pypi/Flask-Caching/"),
        ProjectLink("Source Code", "https://github.com/pallets-eco/Flask-Caching"),
        ProjectLink(
            "Issue Tracker", "https://github.com/pallets-eco/Flask-Caching/issues/"
        ),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}
html_static_path = ["_static"]
html_favicon = "_static/flask-cache.png"
html_logo = "_static/flask-cache.png"
html_title = f"Flask-Caching Documentation ({version})"
html_show_sourcelink = False
