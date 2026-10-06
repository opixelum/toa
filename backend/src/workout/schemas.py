from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SetType(str, Enum):
    WARMUP = "WARMUP"
    WORKSET = "WORKSET"
    DROPSET = "DROPSET"
    SUPERSET = "SUPERSET"
    FAILURE = "FAILURE"


class ExerciseType(str, Enum):
    REPS = "REPS"
    DURATION = "DURATION"


class Equipment(str, Enum):
    BARBELL = "BARBELL"
    DUMBBELL = "DUMBBELL"
    MACHINE = "MACHINE"
    BODYWEIGHT = "BODYWEIGHT"
    ASSISTED_BODYWEIGHT = "ASSISTED_BODYWEIGHT"


# --- User Schemas ---


class UserBase(BaseModel):
    email: str = Field(..., max_length=255)
    bodyweight: float | None = None


class UserCreate(UserBase):
    password: str = Field(..., max_length=255)


class UserUpdate(BaseModel):
    email: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, max_length=255)
    bodyweight: float | None = None


class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


# --- Macrocycle Schemas ---


class MacrocycleBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    nb_mesocycles: int | None = None


class MacrocycleCreate(MacrocycleBase):
    user_id: int


class MacrocycleUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    nb_mesocycles: int | None = None


class MacrocycleRead(MacrocycleBase):
    id: int
    user_id: int
    creation_date: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Mesocycle Schemas ---


class MesocycleBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)


class MesocycleCreate(MesocycleBase):
    macrocycle_id: int


class MesocycleUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    macrocycle_id: int | None = None


class MesocycleRead(MesocycleBase):
    id: int
    macrocycle_id: int
    creation_date: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Workout Schemas ---


class WorkoutBase(BaseModel):
    name: str = Field(..., max_length=255)
    planned: bool = True
    description: str | None = Field(default=None, max_length=1024)
    note: str | None = Field(default=None, max_length=2048)
    rpe: float | None = Field(default=None, ge=1.0, le=10.0)


class WorkoutCreate(WorkoutBase):
    user_id: int
    mesocycle_id: int | None = None
    source_workout_id: int | None = None


class WorkoutUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    planned: bool | None = None
    description: str | None = Field(default=None, max_length=1024)
    note: str | None = Field(default=None, max_length=2048)
    rpe: float | None = Field(default=None, ge=1.0, le=10.0)
    mesocycle_id: int | None = None
    source_workout_id: int | None = None


class WorkoutRead(WorkoutBase):
    id: int
    user_id: int
    mesocycle_id: int | None = None
    source_workout_id: int | None = None
    creation_date: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutVolumeRead(BaseModel):
    workout_id: int
    total_volume: float


# --- Exercise Schemas ---


class ExerciseBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    type: ExerciseType = ExerciseType.REPS
    equipment: Equipment


class ExerciseCreate(ExerciseBase):
    user_id: int


class ExerciseUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    type: ExerciseType | None = None
    equipment: Equipment | None = None


class ExerciseRead(ExerciseBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


# --- WorkoutExercise Schemas ---


class WorkoutExerciseBase(BaseModel):
    position: int = 0
    note: str | None = Field(default=None, max_length=1024)


class WorkoutExerciseCreate(WorkoutExerciseBase):
    workout_id: int
    exercise_id: int


class WorkoutExerciseUpdate(BaseModel):
    position: int | None = None
    note: str | None = Field(default=None, max_length=1024)


class WorkoutExerciseRead(WorkoutExerciseBase):
    id: int
    workout_id: int
    exercise_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Set Schemas ---


class SetBase(BaseModel):
    position: int = 0
    type_: SetType = SetType.WORKSET
    weight: float | None = None
    rpe: float | None = Field(default=None, ge=1.0, le=10.0)
    rest: int = 0


class SetCreate(SetBase):
    workout_id: int
    exercise_id: int


class SetUpdate(BaseModel):
    position: int | None = None
    type_: SetType | None = None
    weight: float | None = None
    rpe: float | None = Field(default=None, ge=1.0, le=10.0)
    rest: int | None = None
    workout_id: int | None = None
    exercise_id: int | None = None


class SetRead(SetBase):
    id: int
    workout_id: int
    exercise_id: int

    model_config = ConfigDict(from_attributes=True)


# --- RepSet Schemas ---


class RepSetBase(SetBase):
    reps: int | None = None


class RepSetCreate(RepSetBase):
    workout_id: int
    exercise_id: int


class RepSetUpdate(BaseModel):
    position: int | None = None
    type_: SetType | None = None
    weight: float | None = None
    rpe: float | None = Field(default=None, ge=1.0, le=10.0)
    rest: int | None = None
    workout_id: int | None = None
    exercise_id: int | None = None
    reps: int | None = None


class RepSetRead(BaseModel):
    id: int
    set_id: int
    type_: str | None = None
    weight: float | None = None
    rpe: float | None = None
    rest: int | None = None
    workout_id: int | None = None
    exercise_id: int | None = None
    position: int = 0
    reps: int | None = None

    model_config = ConfigDict(from_attributes=True)


# --- DurationSet Schemas ---


class DurationSetBase(SetBase):
    duration: int = 0


class DurationSetCreate(DurationSetBase):
    workout_id: int
    exercise_id: int


class DurationSetUpdate(BaseModel):
    position: int | None = None
    type_: SetType | None = None
    weight: float | None = None
    rpe: float | None = Field(default=None, ge=1.0, le=10.0)
    rest: int | None = None
    workout_id: int | None = None
    exercise_id: int | None = None
    duration: int | None = None


class DurationSetRead(BaseModel):
    id: int
    set_id: int
    type_: str | None = None
    weight: float | None = None
    rpe: float | None = None
    rest: int | None = None
    workout_id: int | None = None
    exercise_id: int | None = None
    position: int = 0
    duration: int = 0

    model_config = ConfigDict(from_attributes=True)


# --- Personal Records (PR) Schemas ---


class PersonalRecordRead(BaseModel):
    type: str
    label: str
    value: float
    unit: str
    date: datetime | None = None
    detail: str | None = None


class RepsAtWeightRead(BaseModel):
    weight: float
    reps: int
    date: datetime | None = None


class DurationAtWeightRead(BaseModel):
    weight: float
    duration: int
    date: datetime | None = None


class ExercisePRsRead(BaseModel):
    exercise_id: int
    records: list[PersonalRecordRead]
    reps_per_weight: list[RepsAtWeightRead]
    duration_per_weight: list[DurationAtWeightRead] = Field(default_factory=list)
