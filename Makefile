.PHONY: rebuild
rebuild:
	docker compose build --no-cache django
	docker compose up -d

.PHONY: update
update:
	docker compose exec django pip install -r requirements.txt
	docker compose restart django