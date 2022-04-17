fmt:
	black src/ && isort src/
lint:
	black --check src/ && isort --check src && flake8 src/
test:
	python src/manage.py test
schema:
	python src/manage.py graphql_schema --out schema.json
doc:
	python src/manage.py graphql_schema --out schema.json  && graphdoc -s schema.json -o docs/graphdoc/ --force && gqldoc -s schema.json -o docs/gqldoc/
