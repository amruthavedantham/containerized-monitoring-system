FROM python:3.10-slim

WORKDIR /app

# Keep dependency installation cacheable, while copying the model and service
# source afterward so either one invalidates the runtime image when changed.
COPY ml_service/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ml_service/ /app/ml_service/
COPY load-testing/ /app/load-testing/

WORKDIR /app/ml_service

EXPOSE 5001

CMD ["python", "app.py"]
