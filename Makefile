default: ## Run docker-compose up --detach
	docker-compose -f docker-compose.yml up --detach

dev:  ## Run docker-compose.dev.yml
	docker-compose -f docker-compose.dev.yml up --detach

build-dev: ## Build fts3-client:dev image
	cd app && docker build -t fts3-client:dev .

remove-fts3-image: ## Remove fts3-client:dev image
	docker image rm fts3-client:dev

down-dev: ## Run docker-compose.dev.yml down
	docker-compose -f docker-compose.dev.yml down

enter-fts3: ## Enter fts3-client container
	docker exec -it fts3_client bash

restart-dev: ## Restart fts3_client
	docker-compose -f docker-compose.dev.yml restart fts3_client

logs: ## Follows logs of fts3-client
	docker logs -f fts3_client

help:
	    @egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: help