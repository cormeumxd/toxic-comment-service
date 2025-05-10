FROM python:3.10-slim

WORKDIR /app

COPY ./auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .env .
COPY ./auth-service/app .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]