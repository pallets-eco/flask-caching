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
	python setup.py build_sphinx
	python setup.py upload_sphinx

docs:
	$(MAKE) -C docs html
