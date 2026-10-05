from workout import crud, prs, schemas


def _user(db, email="prs@example.com", bodyweight=80.0):
    return crud.create_user(
        db, schemas.UserCreate(email=email, password="password", bodyweight=bodyweight)
    )


def _workout(db, user_id):
    return crud.create_workout(
        db, schemas.WorkoutCreate(name="PR workout", user_id=user_id, planned=False)
    )


def _exercise(db, user_id, name, type_, equipment):
    return crud.create_exercise(
        db,
        schemas.ExerciseCreate(name=name, user_id=user_id, type=type_, equipment=equipment),
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


def _duration_set(db, workout_id, exercise_id, duration):
    crud.create_duration_set(
        db,
        schemas.DurationSetCreate(
            workout_id=workout_id,
            exercise_id=exercise_id,
            type_=schemas.SetType.WORKSET,
            duration=duration,
        ),
    )


def _record(result, type_):
    return next((r for r in result.records if r.type == type_), None)


def test_barbell_prs(db_session):
    user = _user(db_session, bodyweight=80.0)
    workout = _workout(db_session, user.id)
    exercise = _exercise(
        db_session,
        user.id,
        "Bench Press",
        schemas.ExerciseType.REPS,
        schemas.Equipment.BARBELL,
    )
    _rep_set(db_session, workout.id, exercise.id, 100, 5)
    _rep_set(db_session, workout.id, exercise.id, 110, 3)
    _rep_set(db_session, workout.id, exercise.id, 100, 8)
    _rep_set(db_session, workout.id, exercise.id, 90, 10)

    result = prs.compute_exercise_prs(exercise, user.bodyweight)

    assert result.exercise_id == exercise.id
    assert _record(result, "HEAVIEST_WEIGHT").value == 110.0
    assert abs(_record(result, "ESTIMATED_1RM").value - 126.7) < 0.01
    assert _record(result, "MAX_VOLUME").value == 900.0
    by_weight = {rw.weight: rw.reps for rw in result.reps_per_weight}
    assert by_weight == {90.0: 10, 100.0: 8, 110.0: 3}


def test_assisted_prs(db_session):
    user = _user(db_session)
    workout = _workout(db_session, user.id)
    exercise = _exercise(
        db_session,
        user.id,
        "Assisted Pull-up",
        schemas.ExerciseType.REPS,
        schemas.Equipment.ASSISTED_BODYWEIGHT,
    )
    _rep_set(db_session, workout.id, exercise.id, 20, 8)
    _rep_set(db_session, workout.id, exercise.id, 15, 6)
    _rep_set(db_session, workout.id, exercise.id, 25, 10)

    result = prs.compute_exercise_prs(exercise, user.bodyweight)

    # Least assistance wins
    assert _record(result, "HEAVIEST_WEIGHT").value == 15.0
    # Estimated 1RM is skipped for assisted exercises
    assert _record(result, "ESTIMATED_1RM") is None


def test_bodyweight_prs(db_session):
    user = _user(db_session, bodyweight=80.0)
    workout = _workout(db_session, user.id)
    exercise = _exercise(
        db_session,
        user.id,
        "Pull-up",
        schemas.ExerciseType.REPS,
        schemas.Equipment.BODYWEIGHT,
    )
    _rep_set(db_session, workout.id, exercise.id, None, 12)
    _rep_set(db_session, workout.id, exercise.id, 20, 5)
    _rep_set(db_session, workout.id, exercise.id, 10, 8)

    result = prs.compute_exercise_prs(exercise, user.bodyweight)

    assert _record(result, "ADDITIONAL_WEIGHT").value == 20.0
    assert _record(result, "TOTAL_WEIGHT").value == 100.0  # 80 + 20


def test_duration_prs(db_session):
    user = _user(db_session)
    workout = _workout(db_session, user.id)
    exercise = _exercise(
        db_session,
        user.id,
        "Plank",
        schemas.ExerciseType.DURATION,
        schemas.Equipment.BODYWEIGHT,
    )
    _duration_set(db_session, workout.id, exercise.id, 45)
    _duration_set(db_session, workout.id, exercise.id, 90)

    result = prs.compute_exercise_prs(exercise, user.bodyweight)

    assert _record(result, "LONGEST_DURATION").value == 90.0
    assert result.reps_per_weight == []
