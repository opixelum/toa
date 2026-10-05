"""Compute a workout's total training volume."""

from . import models


def compute_workout_volume(workout: models.Workout) -> float:
    """Return the total volume for a workout, summed across all its sets.

    A rep set contributes ``weight * reps``. For a ``BODYWEIGHT`` exercise the
    load is ``bodyweight + additional weight`` when the owning user has a
    bodyweight set; otherwise the additional weight alone is used. Duration
    sets contribute nothing.
    """
    bodyweight = workout.user.bodyweight if workout.user is not None else None

    total = 0.0
    for set_ in workout.sets:
        rep_set = set_.rep_set
        if rep_set is None:
            continue
        reps = rep_set.reps
        if reps is None or reps <= 0:
            continue
        weight = set_.weight
        is_bodyweight = (
            set_.exercise is not None and set_.exercise.equipment == "BODYWEIGHT"
        )
        if is_bodyweight and bodyweight is not None:
            total += (bodyweight + (weight or 0.0)) * reps
        elif weight is not None and weight > 0:
            total += weight * reps
    return total
