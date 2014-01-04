.PHONY: notebook test dist upload
notebook:
	ipython notebook --pylab=inline example.ipynb

test:
	nosetests image_novice/test

register:
	python setup.py register

dist:
	python setup.py sdist

upload:
	python setup.py sdist upload
