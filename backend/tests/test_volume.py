from workout import crud, schemas, volume


def _user(db, email="volume@example.com", bodyweight: float | None = 80.0):
    return crud.create_user(
        db, schemas.UserCreate(email=email, password="password", bodyweight=bodyweight)
    )


def _workout(db, user_id):
    return crud.create_workout(
        db, schemas.WorkoutCreate(name="Volume workout", user_id=user_id, planned=False)
    )


def _exercise(db, user_id, name, equipment):
    return crud.create_exercise(
        db,
        schemas.ExerciseCreate(
            name=name,
            user_id=user_id,
            type=schemas.ExerciseType.REPS,
            equipment=equipment,
        ),
    )


def _rep_set(db, workout_id, exercise_id, weight, reps):
    crud.create_rep_set(
        db,
        schemas.RepSetCreate(
            workout_id=workout_id,
            exercise_id=exercise_id,
            type_=schemas.SetType.WORKSET,
            weight=weight,
            reps=reps,
        ),
    )


def test_total_workout_volume(db_session):
    user = _user(db_session, bodyweight=80.0)
    workout = _workout(db_session, user.id)
    barbell = _exercise(db_session, user.id, "Bench Press", schemas.Equipment.BARBELL)
    pullup = _exercise(db_session, user.id, "Pull-up", schemas.Equipment.BODYWEIGHT)

    # Barbell: 100 x 5 + 110 x 3 = 500 + 330 = 830
    _rep_set(db_session, workout.id, barbell.id, 100, 5)
    _rep_set(db_session, workout.id, barbell.id, 110, 3)
    # Bodyweight (user = 80kg): (80 + 20) x 5 + (80 + 0) x 12 = 500 + 960 = 1460
    _rep_set(db_session, workout.id, pullup.id, 20, 5)
    _rep_set(db_session, workout.id, pullup.id, None, 12)

    # Total: 830 + 1460 = 2290
    assert volume.compute_workout_volume(workout) == 2290.0


def test_bodyweight_without_bodyweight_uses_added_weight(db_session):
    user = _user(db_session, bodyweight=None)
    workout = _workout(db_session, user.id)
    pullup = _exercise(db_session, user.id, "Pull-up", schemas.Equipment.BODYWEIGHT)

    _rep_set(db_session, workout.id, pullup.id, 20, 5)
    _rep_set(db_session, workout.id, pullup.id, None, 12)

    # No bodyweight set, so only additional weight counts: 20 x 5 = 100
    assert volume.compute_workout_volume(workout) == 100.0


def test_duration_sets_contribute_zero(db_session):
    user = _user(db_session, bodyweight=80.0)
    workout = _workout(db_session, user.id)
    plank = crud.create_exercise(
        db_session,
        schemas.ExerciseCreate(
            name="Plank",
            user_id=user.id,
            type=schemas.ExerciseType.DURATION,
            equipment=schemas.Equipment.BODYWEIGHT,
        ),
    )
    crud.create_duration_set(
        db_session,
        schemas.DurationSetCreate(
            workout_id=workout.id,
            exercise_id=plank.id,
            type_=schemas.SetType.WORKSET,
            duration=90,
        ),
    )

    assert volume.compute_workout_volume(workout) == 0.0
