import os
import time
import random
from locust import HttpUser, LoadTestShape, between, task

SCENARIO = os.getenv("LOCUST_SCENARIO", "normal").strip().lower()


class WebsiteUser(HttpUser):
    """
    Scenario-driven workload for dataset collection and live demonstrations.

    Supported LOCUST_SCENARIO:
    - normal
    - ramp
    - spike
    - heavy
    - demo_latency  (60s: normal -> slow spike -> recover)
    - demo_errors   (60s: normal -> slow+error spike -> recover)
    """

    wait_time = between(0.5, 1.5)

    def get_elapsed_time(self):
        if self.environment and self.environment.runner and self.environment.runner.stats.total.start_time:
            return time.time() - self.environment.runner.stats.total.start_time
        return 0

    @task
    def execute_workload(self):
        elapsed = self.get_elapsed_time()

        if SCENARIO == "demo_latency":
            # 1-minute scenario:
            # 0-20s: normal traffic
            # 20-40s: slow spike (latency rises, errors stay low)
            # 40-60s: recovery
            if 20 <= elapsed < 40:
                if random.random() < 0.80:
                    self.client.get("/slow")
                else:
                    self.client.get("/process")
            else:
                if random.random() < 0.90:
                    self.client.get("/process")
                else:
                    self.client.get("/slow")

        elif SCENARIO == "demo_errors":
            # 1-minute scenario:
            # 0-20s: normal traffic
            # 20-40s: slow + error spike (both latency and error percentage rise)
            # 40-60s: recovery
            if 20 <= elapsed < 40:
                r = random.random()
                if r < 0.45:
                    self.client.get("/error")
                elif r < 0.85:
                    self.client.get("/slow")
                else:
                    self.client.get("/process")
            else:
                if random.random() < 0.90:
                    self.client.get("/process")
                else:
                    self.client.get("/slow")

        elif SCENARIO == "normal":
            if random.random() < 0.90:
                self.client.get("/process")
            else:
                self.client.get("/slow")

        elif SCENARIO == "ramp":
            if random.random() < 0.80:
                self.client.get("/process")
            else:
                self.client.get("/slow")

        elif SCENARIO == "spike":
            r = random.random()
            if r < 0.60:
                self.client.get("/process")
            elif r < 0.90:
                self.client.get("/slow")
            else:
                self.client.get("/error")

        elif SCENARIO == "heavy":
            r = random.random()
            if r < 0.40:
                self.client.get("/process")
            elif r < 0.80:
                self.client.get("/slow")
            else:
                self.client.get("/error")

        else:
            self.client.get("/process")


class ScenarioShape(LoadTestShape):
    """
    Time-based scenario runner so the dataset and demos have clear phase boundaries.
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
        "demo_latency": [
            (20, 10, 5),    # Phase 1: Baseline normal (20s)
            (20, 40, 10),   # Phase 2: Middle spike with slow requests (20s)
            (20, 10, 5),    # Phase 3: Recovery normal (20s)
        ],
        "demo_errors": [
            (20, 10, 5),    # Phase 1: Baseline normal (20s)
            (20, 40, 10),   # Phase 2: Middle spike with slow + error requests (20s)
            (20, 10, 5),    # Phase 3: Recovery normal (20s)
        ],
    }

    def tick(self):
        stages = self.scenario_stages.get(SCENARIO, self.scenario_stages["normal"])
        run_time = self.get_run_time()
        elapsed = 0

        for duration, users, spawn_rate in stages:
            elapsed += duration
            if run_time < elapsed:
                return users, spawn_rate

        return None
