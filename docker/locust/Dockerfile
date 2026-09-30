FROM python:3.10-slim

WORKDIR /locust

RUN pip install --no-cache-dir \
    locust==2.46.0 \
    requests==2.32.2 \
    pandas==2.2.0 \
    numpy==1.26.4

COPY load-testing/locust /locust

EXPOSE 8089

ENV LOCUST_SCENARIO=normal
ENV FLASK_HOST_URL=http://app:5000

CMD ["locust", "-f", "scripts/locustfile.py", "--host", "http://app:5000"]
