from locust import HttpLocust, TaskSet, task

class WebsiteTasks(TaskSet):
    @task
    def index(self):
        self.client.get("/")
        
    @task
    def status(self):
        self.client.get("/status")

    @task
    def hetarchief(self):
        self.client.get("/status/hetarchief.png")

    @task
    def ftp(self):
        self.client.get("/status/ftp.png")

class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000
