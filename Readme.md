# SwimmingDB
This is a simple project I develop in my free time to create a database server based on the django framework to manage a swimming group 

```python manage.py makemigrations```

Create Production
```bash
docker compose -f swimpro-compose.prod.yaml -p swimming-pro up --build
```

Create Dev environment
```bash
docker compose -f swimpro-compose.dev.yaml -p swimming-pro-dev up --build
```