FROM python:3.10-slim

WORKDIR /app

# Copy entire app folder
COPY app /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements/requirements.txt

EXPOSE 5000

CMD ["python", "src/app.py"]
