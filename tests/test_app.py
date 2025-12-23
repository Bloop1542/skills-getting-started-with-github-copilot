import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    new_email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": new_email})
    assert response.status_code == 200
    assert new_email in activities["Chess Club"]["participants"]


def test_signup_for_activity_prevents_duplicates():
    response = client.post(
        "/activities/Programming Class/signup", params={"email": "emma@mergington.edu"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_activity_activity_not_found():
    response = client.post(
        "/activities/Unknown/signup", params={"email": "someone@example.com"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_student():
    response = client.delete(
        "/activities/Basketball/unregister", params={"email": "james@mergington.edu"}
    )
    assert response.status_code == 200
    assert "james@mergington.edu" not in activities["Basketball"]["participants"]


def test_unregister_participant_not_signed_up():
    response = client.delete(
        "/activities/Basketball/unregister", params={"email": "nonexistent@mergington.edu"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_unregister_activity_not_found():
    response = client.delete(
        "/activities/Unknown/unregister", params={"email": "someone@example.com"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
