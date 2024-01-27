grill:
   poetry run pytest
   poetry run mypy .
   isort .
   black .
   ruff . --fix
  
md:
  npx prettier README.md --write