ROOT_DIR := $(shell git rev-parse --show-toplevel)
APP_MODULE := yact
UV := uv
TESTS_DIR := tests


# Default target

all: run

run:		## Run the program
	@echo "Run the program"
	$(UV) run $(APP_MODULE)

test:	## Run unit tests
	@echo "Run all unit tests in Flo 1.0 environment"
	$(UV) run --dev -m pytest -s $(TESTS_DIR)

clean: 		## Clean output files and build cache
	@echo "Removing build cache and files."
	@rm -rf __pycache__
	@rm -rf .cache
	@rm -rf pytest_cache
	@rm -rf dist
	@rm -rf build
	@rm -rf docs/_build
	@rm -rf *.egg-info
	@rm -rf outputs
	@find . -type f -name '*.pyc' -delete

help: Makefile	## Help
	@echo " Usage:\n  make <target>"
	@echo
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
