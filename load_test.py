from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1, 3)  # Время ожидания между запросами

    @task
    def my_task(self):
        self.client.get("/user_banner/admin", headers={"token": "admin"})
