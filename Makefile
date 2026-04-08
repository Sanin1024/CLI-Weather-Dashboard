install:
	pip install -e .

test:
	pytest

build:
	python -m build

publish:
	twine upload dist/*

clean:
	rm -rf dist build *.egg-info