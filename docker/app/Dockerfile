FROM python:3.10-slim

WORKDIR /app

# Copy dependencies first so Docker can cache installation independently of source.
COPY app/requirements/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# These copies are intentionally separate build inputs. Any change to application,
# demo, or Locust source invalidates the image layer used by Compose.
COPY app/ /app/
COPY load-testing/ /load-testing/

EXPOSE 5000

CMD ["python", "src/app.py"]
