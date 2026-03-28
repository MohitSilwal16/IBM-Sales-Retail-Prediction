.PHONY: dev prod

dev:
	docker compose -f compose.dev.yaml down -v
	docker compose -f compose.dev.yaml build --no-cache
	docker compose -f compose.dev.yaml up -w

prod:
	docker compose -f compose.prod.yaml down
	docker compose -f compose.prod.yaml build --no-cache
	docker compose -f compose.prod.yaml up -d
