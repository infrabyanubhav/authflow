import random
import string

from locust import HttpUser, between, task


class AuthUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def test_welcome_endpoint(self):
        """Test the welcome endpoint (most common operation)"""
        self.client.get("/welcome")

    @task(2)
    def test_health_check(self):
        """Test health endpoint"""
        self.client.get("/health")

    @task(1)
    def test_auth_signup(self):
        """Test user signup (less frequent but important)"""
        random_email = (
            f"test_{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"
        )
        random_password = "".join(
            random.choices(string.ascii_letters + string.digits, k=12)
        )

        self.client.post(
            "/auth/signup", json={"email": random_email, "password": random_password}
        )

    def on_start(self):
        """Called when a user starts - good for login simulation"""
        pass
