.PHONY: clean  test pypi docs

test:
	python setup.py test

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

pypi:
	python setup.py sdist bdist_wheel upload

docs:
	$(MAKE) -C docs html
