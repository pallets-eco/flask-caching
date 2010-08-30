test:
	python setup.py test

pypi:
	python setup.py sdist bdist_egg upload
	python setup.py build_sphinx
	python setup.py upload_sphinx
