import os

from locust import HttpUser, LoadTestShape, between, task


SCENARIO = os.getenv("LOCUST_SCENARIO", "normal").strip().lower()


class WebsiteUser(HttpUser):
    """
    Scenario-driven workload for dataset collection.

    Set LOCUST_SCENARIO to one of:
    - normal
    - ramp
    - spike
    - heavy
    """

    wait_time = between(1, 3)

    @task
    def normal_request(self):
        self.client.get("/process")

    @task
    def slow_request(self):
        self.client.get("/slow")

    @task
    def error_request(self):
        self.client.get("/error")


if SCENARIO == "normal":
    WebsiteUser.tasks = (
        [WebsiteUser.normal_request] * 9
        + [WebsiteUser.slow_request] * 1
    )
elif SCENARIO == "ramp":
    WebsiteUser.tasks = (
        [WebsiteUser.normal_request] * 8
        + [WebsiteUser.slow_request] * 2
    )
elif SCENARIO == "spike":
    WebsiteUser.tasks = (
        [WebsiteUser.normal_request] * 6
        + [WebsiteUser.slow_request] * 3
        + [WebsiteUser.error_request] * 1
    )
elif SCENARIO == "heavy":
    WebsiteUser.tasks = (
        [WebsiteUser.normal_request] * 4
        + [WebsiteUser.slow_request] * 4
        + [WebsiteUser.error_request] * 2
    )
else:
    raise ValueError(
        f"Unsupported LOCUST_SCENARIO={SCENARIO!r}. "
        "Use normal, ramp, spike, or heavy."
    )


class ScenarioShape(LoadTestShape):
    """
    Time-based scenario runner so the dataset has clear phase boundaries.
    """

    scenario_stages = {
        "normal": [
            (180, 20, 5),
        ],
        "ramp": [
            (60, 10, 5),
            (120, 25, 5),
            (180, 50, 10),
            (240, 75, 15),
            (300, 100, 20),
        ],
        "spike": [
            (90, 20, 5),
            (150, 200, 20),
            (240, 20, 5),
        ],
        "heavy": [
            (90, 100, 10),
            (180, 200, 20),
            (270, 300, 30),
        ],
    }

    def tick(self):
        stages = self.scenario_stages[SCENARIO]
        run_time = self.get_run_time()
        elapsed = 0

        for duration, users, spawn_rate in stages:
            elapsed += duration
            if run_time < elapsed:
                return users, spawn_rate

        return None
