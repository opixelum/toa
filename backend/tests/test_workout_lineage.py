from workout import crud, schemas


def _create_user(db_session, email: str) -> int:
    user = crud.create_user(
        db_session,
        schemas.UserCreate(email=email, password="password", bodyweight=80.0),
    )
    return user.id


def _create_workout(
    db_session,
    user_id: int,
    name: str,
    planned: bool = True,
    source_workout_id: int | None = None,
) -> int:
    workout = crud.create_workout(
        db_session,
        schemas.WorkoutCreate(
            name=name,
            user_id=user_id,
            planned=planned,
            source_workout_id=source_workout_id,
        ),
    )
    return workout.id


def test_workout_lineage_lifecycle(db_session):
    user_id = _create_user(db_session, "lineage_test@example.com")

    # Create the planned (source) workout.
    source_id = _create_workout(
        db_session, user_id, name="Planned Workout", planned=True
    )
    source = crud.get_workout(db_session, source_id)
    assert source is not None
    assert source.source_workout_id is None
    assert source.derived_workouts == []

    # Create a performed workout derived from the planned one.
    derived_id = _create_workout(
        db_session,
        user_id,
        name="Performed Workout",
        planned=False,
        source_workout_id=source_id,
    )
    derived = crud.get_workout(db_session, derived_id)
    assert derived is not None
    assert derived.source_workout_id == source_id
    assert derived.source_workout is not None
    assert derived.source_workout.id == source_id

    # The source workout reflects the derived workout through the backref.
    db_session.expire_all()
    source = crud.get_workout(db_session, source_id)
    assert source is not None
    assert [w.id for w in source.derived_workouts] == [derived_id]

    # Update the derived workout to detach it from its source.
    crud.update_workout(
        db_session,
        derived_id,
        schemas.WorkoutUpdate(source_workout_id=None),
    )
    updated = crud.get_workout(db_session, derived_id)
    assert updated is not None
    assert updated.source_workout_id is None

    db_session.close()
