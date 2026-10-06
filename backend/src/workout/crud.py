from sqlalchemy.orm import Session

from . import models, schemas

# --- User CRUD ---


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        email=user.email,
        password=user.password,
        bodyweight=user.bodyweight,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, user_id: int, user_in: schemas.UserUpdate
) -> models.User | None:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


# --- Macrocycle CRUD ---


def get_macrocycle(db: Session, macrocycle_id: int) -> models.Macrocycle | None:
    return (
        db.query(models.Macrocycle)
        .filter(models.Macrocycle.id == macrocycle_id)
        .first()
    )


def get_macrocycles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
) -> list[models.Macrocycle]:
    query = db.query(models.Macrocycle)
    if user_id is not None:
        query = query.filter(models.Macrocycle.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def create_macrocycle(
    db: Session, macrocycle: schemas.MacrocycleCreate
) -> models.Macrocycle:
    db_macrocycle = models.Macrocycle(
        name=macrocycle.name,
        user_id=macrocycle.user_id,
        description=macrocycle.description,
        nb_mesocycles=macrocycle.nb_mesocycles,
    )
    db.add(db_macrocycle)
    db.commit()
    db.refresh(db_macrocycle)
    return db_macrocycle


def update_macrocycle(
    db: Session, macrocycle_id: int, macrocycle_in: schemas.MacrocycleUpdate
) -> models.Macrocycle | None:
    db_macrocycle = get_macrocycle(db, macrocycle_id)
    if not db_macrocycle:
        return None
    update_data = macrocycle_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_macrocycle, field, value)
    db.commit()
    db.refresh(db_macrocycle)
    return db_macrocycle


def delete_macrocycle(db: Session, macrocycle_id: int) -> bool:
    db_macrocycle = get_macrocycle(db, macrocycle_id)
    if not db_macrocycle:
        return False
    db.delete(db_macrocycle)
    db.commit()
    return True


# --- Mesocycle CRUD ---


def get_mesocycle(db: Session, mesocycle_id: int) -> models.Mesocycle | None:
    return (
        db.query(models.Mesocycle).filter(models.Mesocycle.id == mesocycle_id).first()
    )


def get_mesocycles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    macrocycle_id: int | None = None,
) -> list[models.Mesocycle]:
    query = db.query(models.Mesocycle)
    if macrocycle_id is not None:
        query = query.filter(models.Mesocycle.macrocycle_id == macrocycle_id)
    return query.offset(skip).limit(limit).all()


def create_mesocycle(
    db: Session,
    mesocycle: schemas.MesocycleCreate,
) -> models.Mesocycle:
    db_mesocycle = models.Mesocycle(
        name=mesocycle.name,
        description=mesocycle.description,
        macrocycle_id=mesocycle.macrocycle_id,
    )
    db.add(db_mesocycle)
    db.commit()
    db.refresh(db_mesocycle)
    return db_mesocycle


def update_mesocycle(
    db: Session, mesocycle_id: int, mesocycle_in: schemas.MesocycleUpdate
) -> models.Mesocycle | None:
    db_mesocycle = get_mesocycle(db, mesocycle_id)
    if not db_mesocycle:
        return None
    update_data = mesocycle_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_mesocycle, field, value)
    db.commit()
    db.refresh(db_mesocycle)
    return db_mesocycle


def delete_mesocycle(db: Session, mesocycle_id: int) -> bool:
    db_mesocycle = get_mesocycle(db, mesocycle_id)
    if not db_mesocycle:
        return False
    db.delete(db_mesocycle)
    db.commit()
    return True


# --- Workout CRUD ---


def get_workout(db: Session, workout_id: int) -> models.Workout | None:
    return db.query(models.Workout).filter(models.Workout.id == workout_id).first()


def get_workouts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
    mesocycle_id: int | None = None,
) -> list[models.Workout]:
    query = db.query(models.Workout)
    if user_id is not None:
        query = query.filter(models.Workout.user_id == user_id)
    if mesocycle_id is not None:
        query = query.filter(models.Workout.mesocycle_id == mesocycle_id)
    return query.offset(skip).limit(limit).all()


def create_workout(
    db: Session,
    workout: schemas.WorkoutCreate,
) -> models.Workout:
    db_workout = models.Workout(
        name=workout.name,
        user_id=workout.user_id,
        planned=workout.planned,
        description=workout.description,
        note=workout.note,
        rpe=workout.rpe,
        mesocycle_id=workout.mesocycle_id,
        source_workout_id=workout.source_workout_id,
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


def update_workout(
    db: Session, workout_id: int, workout_in: schemas.WorkoutUpdate
) -> models.Workout | None:
    db_workout = get_workout(db, workout_id)
    if not db_workout:
        return None
    update_data = workout_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_workout, field, value)
    db.commit()
    db.refresh(db_workout)
    return db_workout


def delete_workout(db: Session, workout_id: int) -> bool:
    db_workout = get_workout(db, workout_id)
    if not db_workout:
        return False
    db.delete(db_workout)
    db.commit()
    return True


# --- Exercise CRUD ---


def get_exercise(db: Session, exercise_id: int) -> models.Exercise | None:
    return db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()


def get_exercises(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
) -> list[models.Exercise]:
    query = db.query(models.Exercise)
    if user_id is not None:
        query = query.filter(models.Exercise.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def create_exercise(
    db: Session,
    exercise: schemas.ExerciseCreate,
) -> models.Exercise:
    db_exercise = models.Exercise(
        name=exercise.name,
        user_id=exercise.user_id,
        description=exercise.description,
        type=exercise.type.value
        if isinstance(exercise.type, schemas.ExerciseType)
        else str(exercise.type),
        equipment=exercise.equipment.value
        if isinstance(exercise.equipment, schemas.Equipment)
        else str(exercise.equipment),
    )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def update_exercise(
    db: Session, exercise_id: int, exercise_in: schemas.ExerciseUpdate
) -> models.Exercise | None:
    db_exercise = get_exercise(db, exercise_id)
    if not db_exercise:
        return None
    update_data = exercise_in.model_dump(exclude_unset=True)
    if "type" in update_data and update_data["type"] is not None:
        type_val = update_data["type"]
        update_data["type"] = (
            type_val.value
            if isinstance(type_val, schemas.ExerciseType)
            else str(type_val)
        )
    if "equipment" in update_data and update_data["equipment"] is not None:
        equipment_val = update_data["equipment"]
        update_data["equipment"] = (
            equipment_val.value
            if isinstance(equipment_val, schemas.Equipment)
            else str(equipment_val)
        )
    for field, value in update_data.items():
        setattr(db_exercise, field, value)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def delete_exercise(db: Session, exercise_id: int) -> bool:
    db_exercise = get_exercise(db, exercise_id)
    if not db_exercise:
        return False
    db.delete(db_exercise)
    db.commit()
    return True


# --- WorkoutExercise CRUD ---


def get_workout_exercise(
    db: Session, workout_exercise_id: int
) -> models.WorkoutExercise | None:
    return (
        db.query(models.WorkoutExercise)
        .filter(models.WorkoutExercise.id == workout_exercise_id)
        .first()
    )


def get_workout_exercises(
    db: Session,
    workout_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[models.WorkoutExercise]:
    query = db.query(models.WorkoutExercise)
    if workout_id is not None:
        query = query.filter(models.WorkoutExercise.workout_id == workout_id)
    return (
        query.order_by(models.WorkoutExercise.position).offset(skip).limit(limit).all()
    )


def create_workout_exercise(
    db: Session,
    workout_exercise: schemas.WorkoutExerciseCreate,
) -> models.WorkoutExercise:
    db_workout_exercise = models.WorkoutExercise(
        workout_id=workout_exercise.workout_id,
        exercise_id=workout_exercise.exercise_id,
        position=workout_exercise.position,
        note=workout_exercise.note,
    )
    db.add(db_workout_exercise)
    db.commit()
    db.refresh(db_workout_exercise)
    return db_workout_exercise


def update_workout_exercise(
    db: Session,
    workout_exercise_id: int,
    workout_exercise_in: schemas.WorkoutExerciseUpdate,
) -> models.WorkoutExercise | None:
    db_workout_exercise = get_workout_exercise(db, workout_exercise_id)
    if not db_workout_exercise:
        return None
    update_data = workout_exercise_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_workout_exercise, field, value)
    db.commit()
    db.refresh(db_workout_exercise)
    return db_workout_exercise


def delete_workout_exercise(db: Session, workout_exercise_id: int) -> bool:
    db_workout_exercise = get_workout_exercise(db, workout_exercise_id)
    if not db_workout_exercise:
        return False
    db.delete(db_workout_exercise)
    db.commit()
    return True


def delete_workout_exercises_by_workout(db: Session, workout_id: int) -> int:
    """Delete all workout_exercise entries for a given workout. Returns count deleted."""
    count = (
        db.query(models.WorkoutExercise)
        .filter(models.WorkoutExercise.workout_id == workout_id)
        .delete()
    )
    db.commit()
    return count


# --- Set CRUD ---


def get_set(db: Session, set_id: int) -> models.Set | None:
    return db.query(models.Set).filter(models.Set.id == set_id).first()


def get_sets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    workout_id: int | None = None,
    exercise_id: int | None = None,
) -> list[models.Set]:
    query = db.query(models.Set)
    if workout_id is not None:
        query = query.filter(models.Set.workout_id == workout_id)
    if exercise_id is not None:
        query = query.filter(models.Set.exercise_id == exercise_id)
    return (
        query.order_by(models.Set.position, models.Set.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_set(db: Session, set_in: schemas.SetCreate) -> models.Set:
    type_val = (
        set_in.type_.value
        if isinstance(set_in.type_, schemas.SetType)
        else str(set_in.type_)
    )
    db_set = models.Set(
        type_=type_val,
        weight=set_in.weight,
        rpe=set_in.rpe,
        rest=set_in.rest,
        position=set_in.position,
        workout_id=set_in.workout_id,
        exercise_id=set_in.exercise_id,
    )
    db.add(db_set)
    db.commit()
    db.refresh(db_set)
    return db_set


def update_set(
    db: Session, set_id: int, set_in: schemas.SetUpdate
) -> models.Set | None:
    db_set = get_set(db, set_id)
    if not db_set:
        return None
    update_data = set_in.model_dump(exclude_unset=True)
    if "type_" in update_data and update_data["type_"] is not None:
        type_val = update_data["type_"]
        update_data["type_"] = (
            type_val.value if isinstance(type_val, schemas.SetType) else str(type_val)
        )
    for field, value in update_data.items():
        setattr(db_set, field, value)
    db.commit()
    db.refresh(db_set)
    return db_set


def delete_set(db: Session, set_id: int) -> bool:
    db_set = get_set(db, set_id)
    if not db_set:
        return False
    db.delete(db_set)
    db.commit()
    return True


# --- RepSet CRUD ---


def get_rep_set(db: Session, rep_set_id: int) -> models.RepSet | None:
    return db.query(models.RepSet).filter(models.RepSet.id == rep_set_id).first()


def get_rep_sets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    workout_id: int | None = None,
) -> list[models.RepSet]:
    query = db.query(models.RepSet).join(models.RepSet.set_)
    if workout_id is not None:
        query = query.filter(models.Set.workout_id == workout_id)
    return (
        query.order_by(models.Set.position, models.Set.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_rep_set(
    db: Session,
    rep_set: schemas.RepSetCreate,
) -> models.RepSet:
    type_val = (
        rep_set.type_.value
        if isinstance(rep_set.type_, schemas.SetType)
        else str(rep_set.type_)
    )
    db_set = models.Set(
        type_=type_val,
        weight=rep_set.weight,
        rpe=rep_set.rpe,
        rest=rep_set.rest,
        position=rep_set.position,
        workout_id=rep_set.workout_id,
        exercise_id=rep_set.exercise_id,
    )
    db.add(db_set)
    db.flush()

    db_rep_set = models.RepSet(
        set_id=db_set.id,
        reps=rep_set.reps,
    )
    db.add(db_rep_set)
    db.commit()
    db.refresh(db_rep_set)
    db.refresh(db_set)
    return db_rep_set


def update_rep_set(
    db: Session, rep_set_id: int, rep_set_in: schemas.RepSetUpdate
) -> models.RepSet | None:
    db_rep_set = get_rep_set(db, rep_set_id)
    if not db_rep_set:
        return None
    update_data = rep_set_in.model_dump(exclude_unset=True)

    # Set table fields
    set_fields = {
        "position",
        "type_",
        "weight",
        "rpe",
        "rest",
        "workout_id",
        "exercise_id",
    }
    if db_rep_set.set_:
        for field in set_fields:
            if field in update_data:
                val = update_data[field]
                if field == "type_" and val is not None:
                    val = val.value if isinstance(val, schemas.SetType) else str(val)
                setattr(db_rep_set.set_, field, val)

    # RepSet table fields
    rep_set_fields = {
        "reps",
    }
    for field in rep_set_fields:
        if field in update_data:
            setattr(db_rep_set, field, update_data[field])

    db.commit()
    db.refresh(db_rep_set)
    return db_rep_set


def delete_rep_set(db: Session, rep_set_id: int) -> bool:
    db_rep_set = get_rep_set(db, rep_set_id)
    if not db_rep_set:
        return False
    if db_rep_set.set_:
        db.delete(db_rep_set.set_)
    else:
        db.delete(db_rep_set)
    db.commit()
    return True


# --- DurationSet CRUD ---


def get_duration_set(db: Session, duration_set_id: int) -> models.DurationSet | None:
    return (
        db.query(models.DurationSet)
        .filter(models.DurationSet.id == duration_set_id)
        .first()
    )


def get_duration_sets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    workout_id: int | None = None,
) -> list[models.DurationSet]:
    query = db.query(models.DurationSet).join(models.DurationSet.set_)
    if workout_id is not None:
        query = query.filter(models.Set.workout_id == workout_id)
    return (
        query.order_by(models.Set.position, models.Set.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_duration_set(
    db: Session,
    duration_set: schemas.DurationSetCreate,
) -> models.DurationSet:
    type_val = (
        duration_set.type_.value
        if isinstance(duration_set.type_, schemas.SetType)
        else str(duration_set.type_)
    )
    db_set = models.Set(
        type_=type_val,
        weight=duration_set.weight,
        rpe=duration_set.rpe,
        rest=duration_set.rest,
        position=duration_set.position,
        workout_id=duration_set.workout_id,
        exercise_id=duration_set.exercise_id,
    )
    db.add(db_set)
    db.flush()

    db_duration_set = models.DurationSet(
        set_id=db_set.id,
        duration=duration_set.duration,
    )
    db.add(db_duration_set)
    db.commit()
    db.refresh(db_duration_set)
    db.refresh(db_set)
    return db_duration_set


def update_duration_set(
    db: Session,
    duration_set_id: int,
    duration_set_in: schemas.DurationSetUpdate,
) -> models.DurationSet | None:
    db_duration_set = get_duration_set(db, duration_set_id)
    if not db_duration_set:
        return None
    update_data = duration_set_in.model_dump(exclude_unset=True)

    # Set table fields
    set_fields = {
        "position",
        "type_",
        "weight",
        "rpe",
        "rest",
        "workout_id",
        "exercise_id",
    }
    if db_duration_set.set_:
        for field in set_fields:
            if field in update_data:
                val = update_data[field]
                if field == "type_" and val is not None:
                    val = val.value if isinstance(val, schemas.SetType) else str(val)
                setattr(db_duration_set.set_, field, val)

    # DurationSet table fields
    if "duration" in update_data:
        db_duration_set.duration = update_data["duration"]

    db.commit()
    db.refresh(db_duration_set)
    return db_duration_set


def delete_duration_set(db: Session, duration_set_id: int) -> bool:
    db_duration_set = get_duration_set(db, duration_set_id)
    if not db_duration_set:
        return False
    if db_duration_set.set_:
        db.delete(db_duration_set.set_)
    else:
        db.delete(db_duration_set)
    db.commit()
    return True
