build:
	docker build -t tapis/ci-catalog .

run: build
	docker run --name catalog --rm -p 5000:5000 tapis/ci-catalog

newshell: build
	docker run --rm -it -p 5000:5000 --entrypoint=bash tapis/ci-catalog

shell:
	docker exec -it catalog bash

down:
	docker-compose down
    
up:
	docker-compose up -d

test:
	docker-compose run --rm catalog pytest

restart: down build up