FROM python:3.10-slim

WORKDIR /app

COPY ./transaction-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .env .
COPY ./transaction-service/app .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]