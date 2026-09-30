FROM python:3.10-slim

WORKDIR /app

# Copy entire app files including dataset for offline training fallback
COPY ml_service /app/ml_service
COPY load-testing /app/load-testing

WORKDIR /app/ml_service

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD ["python", "app.py"]
