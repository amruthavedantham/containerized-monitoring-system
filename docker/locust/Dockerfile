FROM python:3.10-slim

WORKDIR /locust

RUN pip install --no-cache-dir locust requests pandas numpy

COPY load-testing/locust /locust

EXPOSE 8089

ENV LOCUST_SCENARIO=normal
ENV FLASK_HOST_URL=http://app:5000

CMD ["locust", "-f", "scripts/locustfile.py", "--host", "http://app:5000"]
