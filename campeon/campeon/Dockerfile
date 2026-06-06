FROM python:3.12-slim

WORKDIR /app

COPY campeon/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY campeon/ .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
