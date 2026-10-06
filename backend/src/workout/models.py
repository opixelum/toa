from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    bodyweight = Column(Float, nullable=True)

    macrocycles = relationship(
        "Macrocycle", back_populates="user", cascade="all, delete-orphan"
    )
    workouts = relationship(
        "Workout", back_populates="user", cascade="all, delete-orphan"
    )
    exercises = relationship(
        "Exercise", back_populates="user", cascade="all, delete-orphan"
    )


class Macrocycle(Base):
    __tablename__ = "macrocycles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    creation_date = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    nb_mesocycles = Column(Integer, nullable=True)

    user = relationship("User", back_populates="macrocycles")
    mesocycles = relationship(
        "Mesocycle", back_populates="macrocycle", cascade="all, delete-orphan"
    )


class Mesocycle(Base):
    __tablename__ = "mesocycles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    creation_date = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    macrocycle_id = Column(
        Integer, ForeignKey("macrocycles.id", ondelete="CASCADE"), nullable=False
    )

    macrocycle = relationship("Macrocycle", back_populates="mesocycles")
    workouts = relationship(
        "Workout", back_populates="mesocycle", cascade="all, delete-orphan"
    )


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    planned = Column(Boolean, nullable=False, default=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    note = Column(String(2048), nullable=True)
    rpe = Column(Float, nullable=True)
    creation_date = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    mesocycle_id = Column(
        Integer, ForeignKey("mesocycles.id", ondelete="SET NULL"), nullable=True
    )
    source_workout_id = Column(
        Integer, ForeignKey("workouts.id", ondelete="SET NULL"), nullable=True
    )

    user = relationship("User", back_populates="workouts")
    mesocycle = relationship("Mesocycle", back_populates="workouts")
    source_workout = relationship(
        "Workout",
        remote_side=[id],
        back_populates="derived_workouts",
        foreign_keys=[source_workout_id],
    )
    derived_workouts = relationship("Workout", back_populates="source_workout")
    sets = relationship("Set", back_populates="workout", cascade="all, delete-orphan")
    workout_exercises = relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint("name", "user_id", name="uq_exercise_name_per_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    type = Column(String(20), nullable=False, default="REPS")
    equipment = Column(String(50), nullable=False)

    user = relationship("User", back_populates="exercises")
    sets = relationship("Set", back_populates="exercise", cascade="all, delete-orphan")
    workout_exercises = relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint(
            "workout_id",
            "exercise_id",
            "position",
            name="uq_workout_exercise_position",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(
        Integer, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id = Column(
        Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    position = Column(Integer, nullable=False, default=0)
    note = Column(String(1024), nullable=True)

    workout = relationship("Workout", back_populates="workout_exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")


class Set(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(
        Integer, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id = Column(
        Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    position = Column(Integer, nullable=False, default=0)
    type_ = Column(String(20), nullable=False, default="WORKSET")
    weight = Column(Float, nullable=True)
    rpe = Column(Float, nullable=True)
    rest = Column(Integer, nullable=False, default=0)

    workout = relationship("Workout", back_populates="sets")
    exercise = relationship("Exercise", back_populates="sets")
    rep_set = relationship(
        "RepSet", back_populates="set_", uselist=False, cascade="all, delete-orphan"
    )
    duration_set = relationship(
        "DurationSet",
        back_populates="set_",
        uselist=False,
        cascade="all, delete-orphan",
    )


class RepSet(Base):
    __tablename__ = "rep_sets"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(
        Integer,
        ForeignKey("sets.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    reps = Column(Integer, nullable=True)

    set_ = relationship("Set", back_populates="rep_set")

    @property
    def type_(self) -> str | None:
        return self.set_.type_ if self.set_ else None

    @property
    def rpe(self) -> float | None:
        return self.set_.rpe if self.set_ else None

    @property
    def weight(self) -> float | None:
        return self.set_.weight if self.set_ else None

    @property
    def rest(self) -> int | None:
        return self.set_.rest if self.set_ else None

    @property
    def position(self) -> int | None:
        return self.set_.position if self.set_ else None

    @property
    def exercise_id(self) -> int | None:
        return self.set_.exercise_id if self.set_ else None

    @property
    def workout_id(self) -> int | None:
        return self.set_.workout_id if self.set_ else None


class DurationSet(Base):
    __tablename__ = "duration_sets"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(
        Integer,
        ForeignKey("sets.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    duration = Column(Integer, nullable=False, default=0)

    set_ = relationship("Set", back_populates="duration_set")

    @property
    def type_(self) -> str | None:
        return self.set_.type_ if self.set_ else None

    @property
    def rpe(self) -> float | None:
        return self.set_.rpe if self.set_ else None

    @property
    def weight(self) -> float | None:
        return self.set_.weight if self.set_ else None

    @property
    def rest(self) -> int | None:
        return self.set_.rest if self.set_ else None

    @property
    def position(self) -> int | None:
        return self.set_.position if self.set_ else None

    @property
    def exercise_id(self) -> int | None:
        return self.set_.exercise_id if self.set_ else None

    @property
    def workout_id(self) -> int | None:
        return self.set_.workout_id if self.set_ else None
