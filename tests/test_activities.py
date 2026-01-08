from fastapi.testclient import TestClient
import copy

import src.app as app_module

client = TestClient(app_module.app)


def setup_function():
    # Save a deep copy of the original activities state so tests can mutate safely
    app_module._activities_backup = copy.deepcopy(app_module.activities)


def teardown_function():
    # Restore activities after each test
    app_module.activities = app_module._activities_backup


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_remove_participant():
    activity = "Basketball"
    email = "tester@mergington.edu"

    # Ensure activity exists and participant not present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Verify participant was added
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Remove participant
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert "Removed" in resp.json()["message"]

    # Verify participant removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_signup_duplicate():
    activity = "Chess Club"
    email = "duplicate@mergington.edu"

    # First signup should succeed
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200

    # Second signup should return 400
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400


def test_signup_full():
    activity = "Tennis Club"
    email1 = "a@mergington.edu"
    email2 = "b@mergington.edu"

    # Make activity have max_participants 1 and fill it
    app_module.activities[activity]["max_participants"] = 1
    app_module.activities[activity]["participants"] = [email1]

    # Attempt to sign up another participant should fail
    resp = client.post(f"/activities/{activity}/signup?email={email2}")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Activity is full"
