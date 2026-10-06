import pytest
from fastapi.testclient import TestClient

from workout.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_api_full_flow(client):
    # 0. Create User
    resp = client.post(
        "/users",
        json={
            "email": "test@example.com",
            "password": "password123",
            "bodyweight": 80.5,
        },
    )
    assert resp.status_code == 201
    user_data = resp.json()
    user_id = user_data["id"]

    # 1. Create Macrocycle
    resp = client.post(
        "/macrocycles", json={"name": "API Test Macrocycle", "user_id": user_id}
    )
    assert resp.status_code == 201
    macro_data = resp.json()
    macro_id = macro_data["id"]
    assert macro_data["name"] == "API Test Macrocycle"

    # Get Macrocycle
    resp = client.get(f"/macrocycles/{macro_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == macro_id

    # 2. Create Mesocycle
    resp = client.post(
        "/mesocycles", json={"name": "API Test Mesocycle", "macrocycle_id": macro_id}
    )
    assert resp.status_code == 201
    meso_data = resp.json()
    meso_id = meso_data["id"]
    assert meso_data["macrocycle_id"] == macro_id

    # 3. Create Workout
    resp = client.post(
        "/workouts",
        json={
            "name": "API Test Workout",
            "user_id": user_id,
            "mesocycle_id": meso_id,
            "note": "Initial test note",
        },
    )
    assert resp.status_code == 201
    workout_data = resp.json()
    workout_id = workout_data["id"]
    assert workout_data["mesocycle_id"] == meso_id
    assert workout_data["note"] == "Initial test note"

    # 4. Create Exercise
    resp = client.post(
        "/exercises",
        json={
            "name": "API Test Bench Press",
            "user_id": user_id,
            "description": "API Test Description",
            "type": "REPS",
            "equipment": "BARBELL",
        },
    )
    assert resp.status_code == 201
    exercise_data = resp.json()
    exercise_id = exercise_data["id"]
    assert exercise_data["equipment"] == "BARBELL"

    resp = client.post(
        "/workout_exercises",
        json={"workout_id": workout_id, "exercise_id": exercise_id, "position": 0},
    )
    assert resp.status_code == 201
    assert resp.json()["exercise_id"] == exercise_id

    # Update Exercise equipment
    resp = client.put(
        f"/exercises/{exercise_id}",
        json={"equipment": "DUMBBELL"},
    )
    assert resp.status_code == 200
    assert resp.json()["equipment"] == "DUMBBELL"

    # 5. Create RepSet
    resp = client.post(
        "/rep_sets",
        json={
            "workout_id": workout_id,
            "exercise_id": exercise_id,
            "type_": "WORKSET",
            "rpe": 9.0,
            "weight": 100.0,
            "rest": 120,
            "reps": 8,
        },
    )
    assert resp.status_code == 201
    repset_data = resp.json()
    repset_id = repset_data["id"]
    assert repset_data["reps"] == 8

    # Update RepSet
    resp = client.put(
        f"/rep_sets/{repset_id}",
        json={"reps": 10, "weight": 105.0, "rpe": 9.5},
    )
    assert resp.status_code == 200
    assert resp.json()["reps"] == 10

    # 6. Create DurationSet
    resp = client.post(
        "/duration_sets",
        json={
            "workout_id": workout_id,
            "exercise_id": exercise_id,
            "type_": "WORKSET",
            "rpe": 7.0,
            "weight": 0.0,
            "rest": 60,
            "duration": 60,
        },
    )
    assert resp.status_code == 201
    dur_data = resp.json()
    dur_id = dur_data["id"]
    assert dur_id is not None
    assert dur_data["duration"] == 60

    # 7. List entities
    assert len(client.get(f"/macrocycles?user_id={user_id}").json()) >= 1
    assert len(client.get(f"/mesocycles?macrocycle_id={macro_id}").json()) == 1
    assert len(client.get(f"/workouts?mesocycle_id={meso_id}").json()) == 1
    assert len(client.get(f"/exercises?user_id={user_id}").json()) >= 1
    assert len(client.get("/rep_sets").json()) >= 1
    assert len(client.get("/duration_sets").json()) >= 1
    assert len(client.get(f"/rep_sets?workout_id={workout_id}").json()) == 1
    assert len(client.get(f"/duration_sets?workout_id={workout_id}").json()) == 1
    workout_exercises = client.get(f"/workout_exercises?workout_id={workout_id}").json()
    assert [item["exercise_id"] for item in workout_exercises] == [exercise_id]

    # The RepSet ID sequence can diverge from parent Set IDs when other set
    # types are inserted; route updates must target the RepSet ID only.
    for reps in (5, 6):
        assert (
            client.post(
                "/rep_sets",
                json={
                    "workout_id": workout_id,
                    "exercise_id": exercise_id,
                    "type_": "WORKSET",
                    "weight": 80.0,
                    "reps": reps,
                },
            ).status_code
            == 201
        )
    resp = client.patch("/rep_sets/3", json={"weight": 123.0})
    assert resp.status_code == 200
    assert resp.json()["id"] == 3
    assert resp.json()["weight"] == 123.0

    # 8. Clean up: Delete User (cascades)
    resp = client.delete(f"/users/{user_id}")
    assert resp.status_code == 204

    # Verify 404 after deletion
    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 404
