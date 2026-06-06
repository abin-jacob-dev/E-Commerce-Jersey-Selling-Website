FROM python:3.12-slim

WORKDIR /app

COPY campeon/ /app/

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
