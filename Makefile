.PHONY: install
install: ## Install with the poetry and add pre-commit hooks
	@echo "🚀 Installing packages with poetry"
	@poetry install
	@poetry run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking Poetry lock file consistency with 'pyproject.toml': Running poetry lock --check"
	@poetry lock --check
	@echo "🚀 Linting code: Running pre-commit"
	@poetry run pre-commit run -a

.PHONY: doc
doc: ## Build sphinx documentation website locally
	@echo "📖 Building documentation"
	@cd docs
	@poetry run sphinx-apidoc -d 3 -f -o docs/api gimie
	@poetry run sphinx-build docs/ docs/_build

.PHONY: docker-build
docker-build: ## Build the gimie Docker image
	@echo "🐋 Building docker image"
	@docker build -t gimie -f .docker/Dockerfile .

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@poetry run pytest

.PHONY: changelog
changelog: ## Generate the changelog
	@git-cliff -l -c pyproject.toml || echo "git-cliff must be installed"

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
