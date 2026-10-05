from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import auth, crud, prs, schemas
from .database import engine, get_db
from .models import Base, User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workout API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DbSession = Annotated[Session, Depends(get_db)]


# --- Users ---


@app.post(
    "/users",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: schemas.UserCreate, db: DbSession):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    # Hash password before creating user
    hashed_password = auth.get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password
    return crud.create_user(db, schemas.UserCreate(**user_dict))


@app.get("/users", response_model=list[schemas.UserRead])
def read_users(db: DbSession, skip: int = 0, limit: int = 100):
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: DbSession):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@app.put("/users/{user_id}", response_model=schemas.UserRead)
def update_user_put(user_id: int, user_in: schemas.UserUpdate, db: DbSession):
    user = crud.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@app.patch("/users/{user_id}", response_model=schemas.UserRead)
def update_user_patch(user_id: int, user_in: schemas.UserUpdate, db: DbSession):
    user = crud.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DbSession):
    if not crud.delete_user(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


# --- Authentication ---


@app.post(
    "/auth/signup", response_model=schemas.Token, status_code=status.HTTP_201_CREATED
)
def signup(user: schemas.UserCreate, db: DbSession):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    # Hash password before creating user
    hashed_password = auth.get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password
    created_user = crud.create_user(db, schemas.UserCreate(**user_dict))

    # Generate token for the new user
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(created_user.id)}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.post("/auth/login", response_model=schemas.Token)
def login(login_data: schemas.LoginRequest, db: DbSession):
    user = auth.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.get("/auth/me", response_model=schemas.UserRead)
def read_users_me(current_user: Annotated[User, Depends(auth.get_current_user)]):
    return current_user


# --- Macrocycles ---


@app.post(
    "/macrocycles",
    response_model=schemas.MacrocycleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_macrocycle(macrocycle: schemas.MacrocycleCreate, db: DbSession):
    return crud.create_macrocycle(db, macrocycle)


@app.get("/macrocycles", response_model=list[schemas.MacrocycleRead])
def read_macrocycles(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
):
    return crud.get_macrocycles(db, skip=skip, limit=limit, user_id=user_id)


@app.get("/macrocycles/{macrocycle_id}", response_model=schemas.MacrocycleRead)
def read_macrocycle(macrocycle_id: int, db: DbSession):
    macrocycle = crud.get_macrocycle(db, macrocycle_id)
    if not macrocycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Macrocycle not found"
        )
    return macrocycle


@app.put("/macrocycles/{macrocycle_id}", response_model=schemas.MacrocycleRead)
def update_macrocycle_put(
    macrocycle_id: int,
    macrocycle_in: schemas.MacrocycleUpdate,
    db: DbSession,
):
    macrocycle = crud.update_macrocycle(db, macrocycle_id, macrocycle_in)
    if not macrocycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Macrocycle not found"
        )
    return macrocycle


@app.patch("/macrocycles/{macrocycle_id}", response_model=schemas.MacrocycleRead)
def update_macrocycle_patch(
    macrocycle_id: int,
    macrocycle_in: schemas.MacrocycleUpdate,
    db: DbSession,
):
    macrocycle = crud.update_macrocycle(db, macrocycle_id, macrocycle_in)
    if not macrocycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Macrocycle not found"
        )
    return macrocycle


@app.delete("/macrocycles/{macrocycle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_macrocycle(macrocycle_id: int, db: DbSession):
    if not crud.delete_macrocycle(db, macrocycle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Macrocycle not found"
        )


# --- Mesocycles ---


@app.post(
    "/mesocycles",
    response_model=schemas.MesocycleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_mesocycle(mesocycle: schemas.MesocycleCreate, db: DbSession):
    return crud.create_mesocycle(db, mesocycle)


@app.get("/mesocycles", response_model=list[schemas.MesocycleRead])
def read_mesocycles(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
    macrocycle_id: int | None = None,
):
    return crud.get_mesocycles(db, skip=skip, limit=limit, macrocycle_id=macrocycle_id)


@app.get("/mesocycles/{mesocycle_id}", response_model=schemas.MesocycleRead)
def read_mesocycle(mesocycle_id: int, db: DbSession):
    mesocycle = crud.get_mesocycle(db, mesocycle_id)
    if not mesocycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mesocycle not found"
        )
    return mesocycle


@app.put("/mesocycles/{mesocycle_id}", response_model=schemas.MesocycleRead)
def update_mesocycle_put(
    mesocycle_id: int,
    mesocycle_in: schemas.MesocycleUpdate,
    db: DbSession,
):
    mesocycle = crud.update_mesocycle(db, mesocycle_id, mesocycle_in)
    if not mesocycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mesocycle not found"
        )
    return mesocycle


@app.patch("/mesocycles/{mesocycle_id}", response_model=schemas.MesocycleRead)
def update_mesocycle_patch(
    mesocycle_id: int,
    mesocycle_in: schemas.MesocycleUpdate,
    db: DbSession,
):
    mesocycle = crud.update_mesocycle(db, mesocycle_id, mesocycle_in)
    if not mesocycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mesocycle not found"
        )
    return mesocycle


@app.delete("/mesocycles/{mesocycle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mesocycle(mesocycle_id: int, db: DbSession):
    if not crud.delete_mesocycle(db, mesocycle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mesocycle not found"
        )


# --- Workouts ---


@app.post(
    "/workouts",
    response_model=schemas.WorkoutRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workout(workout: schemas.WorkoutCreate, db: DbSession):
    return crud.create_workout(db, workout)


@app.get("/workouts", response_model=list[schemas.WorkoutRead])
def read_workouts(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
    mesocycle_id: int | None = None,
):
    return crud.get_workouts(
        db, skip=skip, limit=limit, user_id=user_id, mesocycle_id=mesocycle_id
    )


@app.get("/workouts/{workout_id}", response_model=schemas.WorkoutRead)
def read_workout(workout_id: int, db: DbSession):
    workout = crud.get_workout(db, workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )
    return workout


@app.put("/workouts/{workout_id}", response_model=schemas.WorkoutRead)
def update_workout_put(
    workout_id: int,
    workout_in: schemas.WorkoutUpdate,
    db: DbSession,
):
    workout = crud.update_workout(db, workout_id, workout_in)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )
    return workout


@app.patch("/workouts/{workout_id}", response_model=schemas.WorkoutRead)
def update_workout_patch(
    workout_id: int,
    workout_in: schemas.WorkoutUpdate,
    db: DbSession,
):
    workout = crud.update_workout(db, workout_id, workout_in)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )
    return workout


@app.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, db: DbSession):
    if not crud.delete_workout(db, workout_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )


# --- Exercises ---


@app.post(
    "/exercises",
    response_model=schemas.ExerciseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_exercise(exercise: schemas.ExerciseCreate, db: DbSession):
    return crud.create_exercise(db, exercise)


@app.get("/exercises", response_model=list[schemas.ExerciseRead])
def read_exercises(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
):
    return crud.get_exercises(db, skip=skip, limit=limit, user_id=user_id)


@app.get("/exercises/{exercise_id}", response_model=schemas.ExerciseRead)
def read_exercise(exercise_id: int, db: DbSession):
    exercise = crud.get_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )
    return exercise


@app.put("/exercises/{exercise_id}", response_model=schemas.ExerciseRead)
def update_exercise_put(
    exercise_id: int,
    exercise_in: schemas.ExerciseUpdate,
    db: DbSession,
):
    exercise = crud.update_exercise(db, exercise_id, exercise_in)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )
    return exercise


@app.patch("/exercises/{exercise_id}", response_model=schemas.ExerciseRead)
def update_exercise_patch(
    exercise_id: int,
    exercise_in: schemas.ExerciseUpdate,
    db: DbSession,
):
    exercise = crud.update_exercise(db, exercise_id, exercise_in)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )
    return exercise


@app.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: int, db: DbSession):
    if not crud.delete_exercise(db, exercise_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )


@app.get("/exercises/{exercise_id}/prs", response_model=schemas.ExercisePRsRead)
def read_exercise_prs(exercise_id: int, db: DbSession):
    exercise = crud.get_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )
    bodyweight = exercise.user.bodyweight if exercise.user else None
    return prs.compute_exercise_prs(exercise, bodyweight)


# --- WorkoutExercises ---


@app.post(
    "/workout_exercises",
    response_model=schemas.WorkoutExerciseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workout_exercise(
    workout_exercise: schemas.WorkoutExerciseCreate, db: DbSession
):
    return crud.create_workout_exercise(db, workout_exercise)


@app.get("/workout_exercises", response_model=list[schemas.WorkoutExerciseRead])
def read_workout_exercises(
    db: DbSession,
    workout_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    return crud.get_workout_exercises(db, workout_id=workout_id, skip=skip, limit=limit)


@app.get(
    "/workout_exercises/{workout_exercise_id}",
    response_model=schemas.WorkoutExerciseRead,
)
def read_workout_exercise(workout_exercise_id: int, db: DbSession):
    workout_exercise = crud.get_workout_exercise(db, workout_exercise_id)
    if not workout_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WorkoutExercise not found",
        )
    return workout_exercise


@app.put(
    "/workout_exercises/{workout_exercise_id}",
    response_model=schemas.WorkoutExerciseRead,
)
def update_workout_exercise_put(
    workout_exercise_id: int,
    workout_exercise_in: schemas.WorkoutExerciseUpdate,
    db: DbSession,
):
    workout_exercise = crud.update_workout_exercise(
        db, workout_exercise_id, workout_exercise_in
    )
    if not workout_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WorkoutExercise not found",
        )
    return workout_exercise


@app.patch(
    "/workout_exercises/{workout_exercise_id}",
    response_model=schemas.WorkoutExerciseRead,
)
def update_workout_exercise_patch(
    workout_exercise_id: int,
    workout_exercise_in: schemas.WorkoutExerciseUpdate,
    db: DbSession,
):
    workout_exercise = crud.update_workout_exercise(
        db, workout_exercise_id, workout_exercise_in
    )
    if not workout_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WorkoutExercise not found",
        )
    return workout_exercise


@app.delete(
    "/workout_exercises/{workout_exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_workout_exercise(workout_exercise_id: int, db: DbSession):
    if not crud.delete_workout_exercise(db, workout_exercise_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WorkoutExercise not found",
        )


# --- Sets ---


@app.post(
    "/sets",
    response_model=schemas.SetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_set(set_in: schemas.SetCreate, db: DbSession):
    return crud.create_set(db, set_in)


@app.get("/sets", response_model=list[schemas.SetRead])
def read_sets(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
    workout_id: int | None = None,
    exercise_id: int | None = None,
):
    return crud.get_sets(
        db, skip=skip, limit=limit, workout_id=workout_id, exercise_id=exercise_id
    )


@app.get("/sets/{set_id}", response_model=schemas.SetRead)
def read_set(set_id: int, db: DbSession):
    db_set = crud.get_set(db, set_id)
    if not db_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Set not found"
        )
    return db_set


@app.put("/sets/{set_id}", response_model=schemas.SetRead)
def update_set_put(set_id: int, set_in: schemas.SetUpdate, db: DbSession):
    db_set = crud.update_set(db, set_id, set_in)
    if not db_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Set not found"
        )
    return db_set


@app.patch("/sets/{set_id}", response_model=schemas.SetRead)
def update_set_patch(set_id: int, set_in: schemas.SetUpdate, db: DbSession):
    db_set = crud.update_set(db, set_id, set_in)
    if not db_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Set not found"
        )
    return db_set


@app.delete("/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set(set_id: int, db: DbSession):
    if not crud.delete_set(db, set_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Set not found"
        )


# --- RepSets ---


@app.post(
    "/rep_sets",
    response_model=schemas.RepSetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_rep_set(rep_set: schemas.RepSetCreate, db: DbSession):
    return crud.create_rep_set(db, rep_set)


@app.get("/rep_sets", response_model=list[schemas.RepSetRead])
def read_rep_sets(db: DbSession, skip: int = 0, limit: int = 100):
    return crud.get_rep_sets(db, skip=skip, limit=limit)


@app.get("/rep_sets/{rep_set_id}", response_model=schemas.RepSetRead)
def read_rep_set(rep_set_id: int, db: DbSession):
    db_rep_set = crud.get_rep_set(db, rep_set_id)
    if not db_rep_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="RepSet not found"
        )
    return db_rep_set


@app.put("/rep_sets/{rep_set_id}", response_model=schemas.RepSetRead)
def update_rep_set_put(
    rep_set_id: int,
    rep_set_in: schemas.RepSetUpdate,
    db: DbSession,
):
    db_rep_set = crud.update_rep_set(db, rep_set_id, rep_set_in)
    if not db_rep_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="RepSet not found"
        )
    return db_rep_set


@app.patch("/rep_sets/{rep_set_id}", response_model=schemas.RepSetRead)
def update_rep_set_patch(
    rep_set_id: int,
    rep_set_in: schemas.RepSetUpdate,
    db: DbSession,
):
    db_rep_set = crud.update_rep_set(db, rep_set_id, rep_set_in)
    if not db_rep_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="RepSet not found"
        )
    return db_rep_set


@app.delete("/rep_sets/{rep_set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rep_set(rep_set_id: int, db: DbSession):
    if not crud.delete_rep_set(db, rep_set_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="RepSet not found"
        )


# --- DurationSets ---


@app.post(
    "/duration_sets",
    response_model=schemas.DurationSetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_duration_set(duration_set: schemas.DurationSetCreate, db: DbSession):
    return crud.create_duration_set(db, duration_set)


@app.get("/duration_sets", response_model=list[schemas.DurationSetRead])
def read_duration_sets(db: DbSession, skip: int = 0, limit: int = 100):
    return crud.get_duration_sets(db, skip=skip, limit=limit)


@app.get("/duration_sets/{duration_set_id}", response_model=schemas.DurationSetRead)
def read_duration_set(duration_set_id: int, db: DbSession):
    db_duration_set = crud.get_duration_set(db, duration_set_id)
    if not db_duration_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DurationSet not found",
        )
    return db_duration_set


@app.put("/duration_sets/{duration_set_id}", response_model=schemas.DurationSetRead)
def update_duration_set_put(
    duration_set_id: int,
    duration_set_in: schemas.DurationSetUpdate,
    db: DbSession,
):
    db_duration_set = crud.update_duration_set(db, duration_set_id, duration_set_in)
    if not db_duration_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DurationSet not found",
        )
    return db_duration_set


@app.patch("/duration_sets/{duration_set_id}", response_model=schemas.DurationSetRead)
def update_duration_set_patch(
    duration_set_id: int,
    duration_set_in: schemas.DurationSetUpdate,
    db: DbSession,
):
    db_duration_set = crud.update_duration_set(db, duration_set_id, duration_set_in)
    if not db_duration_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DurationSet not found",
        )
    return db_duration_set


@app.delete("/duration_sets/{duration_set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_duration_set(duration_set_id: int, db: DbSession):
    if not crud.delete_duration_set(db, duration_set_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DurationSet not found",
        )
