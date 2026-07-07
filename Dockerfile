FROM python:3.12-slim

WORKDIR /app

COPY service/requirements.txt service/requirements.txt
RUN pip install --no-cache-dir -r service/requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn service.main:app --host 0.0.0.0 --port $PORT"]
