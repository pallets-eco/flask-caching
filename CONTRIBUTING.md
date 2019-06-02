# How to contribute

The preferred (and easiest) way is to fork the repository, add your changes
based on the `master` branch and create a pull request.

We use Travis CI for continuous integration so all pull requests are
automatically tested for all supported Python versions.

# Setting up the project

After cloning the repository you should need to create a Python virtualenv:

    $ cd flask-caching
    $ python3 -m venv .venv/

This will create a directory `.venv` that you can activate with one of these
commands (depending on your shell):

    $ source .venv/bin/activate       # for Bash and compatible
    $ source .venv/bin/activate.csh   # for C shells like CSH or TCSH
    $ source .venv/bin/activate.fish  # For Fish

The `.venv` directory is on the ignore list, so you can’t accidentally add it
to version control.

Next, you should install the project’s dependencies:

    $ pip install -r requirements.txt

# Formatting code

To avoid getting a “please reformat/break this line” type of message during
reviews, you should run the modified files through
[black](https://github.com/python/black). We usually run it as `black -l 80`,
but a plain `black` will suffice, too. If you have
[pre-commit](https://pre-commit.com/) installed, this is done automatically
for you (just don’t forget to activate it with `pre-commit install`). If you
don’t, you can install `black` manually using

    $ pip install black

# Writing and running tests

Newly added code should be fully tested; otherwise we won’t merge your pull
requests.

Running tests is as easy as

    $ pytest

We have the coverage module enabled so you will see your tests’ coverage
immediately.

If you want to test your changes for other Python versions, install and run `tox`:

    $ pip install tox
    $ tox              # To run for every supported version
    $ tox -e py35      # To run only for Python 3.5

# Helping out without writing code

Besides code, we’re happy to accept pull requests to update documentation,
triage issues, and testing new features before they get merged.

# First-time contributors

If you are a new contributor, look for the [good first
issue](labels/good+first+issue) label. It marks issues that are easy to solve
without thoroughly understanding the code base.
