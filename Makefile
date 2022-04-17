fmt:
	black src/ && isort src/
lint:
	black --check src/ && isort --check src && flake8 src/
test:
	python src/manage.py test
schema:
	python src/manage.py graphql_schema --out docs/schema.graphql
doc:
	python src/manage.py graphql_schema --out schema.graphql && graphdoc -s schema.graphql -o docs/ --force
