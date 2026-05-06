FROM python:3.10-slim

WORKDIR /locust

RUN pip install locust

COPY load-testing/locust/scripts /locust

EXPOSE 8089

CMD ["locust", "-f", "locustfile.py", "--host=http://app:5000"]