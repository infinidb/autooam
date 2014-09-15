default: clean test

clean:
	find . -name "*.pyc" | xargs rm -f

test:
	python -m unittest discover autooam/test/ '*.py' autooam/test/

