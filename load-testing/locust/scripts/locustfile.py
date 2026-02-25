from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task(7)
    def normal_request(self):
        self.client.get("/process")

    @task(2)
    def slow_request(self):
        self.client.get("/slow")

    @task(1)
    def error_request(self):
        self.client.get("/error")
