grill:
   poetry run pytest
   poetry run mypy .
   poetry run isort . --float-to-top
   poetry run black .
   poetry run ruff . --fix
  
md:
  npx prettier README.md --write