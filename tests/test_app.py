from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(deepcopy(initial_activities))


class TestApp:
    def setup_method(self):
        reset_activities()

    def test_get_activities(self):
        response = client.get("/activities")
        assert response.status_code == 200

        data = response.json()
        assert "Chess Club" in data
        assert data["Chess Club"]["description"].startswith("Learn strategies")
        assert isinstance(data["Chess Club"]["participants"], list)

    def test_signup_for_activity(self):
        email = "newstudent@mergington.edu"
        response = client.post("/activities/Chess Club/signup", params={"email": email})

        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for Chess Club"
        assert email in activities["Chess Club"]["participants"]

    def test_duplicate_signup_returns_400(self):
        email = "michael@mergington.edu"
        response = client.post("/activities/Chess Club/signup", params={"email": email})

        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_remove_participant(self):
        email = "michael@mergington.edu"
        response = client.delete(f"/activities/Chess Club/participants/{email}")

        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from Chess Club"
        assert email not in activities["Chess Club"]["participants"]

    def test_remove_missing_participant_returns_404(self):
        email = "missing@mergington.edu"
        response = client.delete(f"/activities/Chess Club/participants/{email}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
