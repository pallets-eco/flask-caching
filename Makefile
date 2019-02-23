.PHONY: test tox clean wheel upload docs

test:
	pytest

tox:
	@tox

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

wheel:
	python setup.py sdist bdist_wheel

upload:
	twine upload dist/* --skip-existing

docs:
	$(MAKE) -C docs html
