FROM python:3.10-slim

WORKDIR /app

# Copy app folder and load-testing folder
COPY app /app
COPY load-testing /load-testing

# Install dependencies
RUN pip install --no-cache-dir -r requirements/requirements.txt

EXPOSE 5000

CMD ["python", "src/app.py"]
