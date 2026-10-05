"""Compute personal records (PRs) for an exercise from its set history."""

from datetime import datetime

from . import models, schemas


def _workout_date(set_: models.Set) -> datetime | None:
    if set_.workout is not None:
        return set_.workout.creation_date
    return None


def _make_record(
    type_: str,
    label: str,
    value: float,
    unit: str,
    date: datetime | None,
) -> schemas.PersonalRecordRead:
    return schemas.PersonalRecordRead(
        type=type_, label=label, value=value, unit=unit, date=date
    )


def compute_exercise_prs(
    exercise: models.Exercise, bodyweight: float | None
) -> schemas.ExercisePRsRead:
    """Compute every personal record for a single exercise.

    ``bodyweight`` is the owning user's bodyweight (used only for bodyweight
    exercises). Records and the per-weight rep breakdown are derived entirely
    from the exercise's existing sets — nothing is stored.
    """
    records: list[schemas.PersonalRecordRead] = []
    sets = list(exercise.sets)

    rep_sets = [
        s for s in sets if s.rep_set is not None and s.rep_set.reps is not None
    ]
    duration_sets = [s for s in sets if s.duration_set is not None]

    is_duration = exercise.type == "DURATION"
    is_assisted = exercise.equipment == "ASSISTED_BODYWEIGHT"
    is_bodyweight = exercise.equipment == "BODYWEIGHT"

    # --- Duration-based exercises: longest duration only ---
    if is_duration:
        best: tuple[float, datetime | None] | None = None
        for s in duration_sets:
            duration = s.duration_set.duration
            if duration is None or duration <= 0:
                continue
            if best is None or duration > best[0]:
                best = (float(duration), _workout_date(s))
        if best is not None:
            records.append(
                _make_record(
                    "LONGEST_DURATION", "Longest duration", best[0], "s", best[1]
                )
            )
        return schemas.ExercisePRsRead(
            exercise_id=exercise.id, records=records, reps_per_weight=[]
        )

    # --- Rep-based exercises ---
    weighted = [
        (s.weight, _workout_date(s))
        for s in rep_sets
        if s.weight is not None and s.weight > 0
    ]

    # Heaviest weight / least assistance / bodyweight split
    if is_bodyweight:
        if weighted:
            value, date = max(weighted, key=lambda item: item[0])
            records.append(
                _make_record(
                    "ADDITIONAL_WEIGHT", "Additional weight", value, "kg", date
                )
            )
        if bodyweight is not None:
            totals = [
                (bodyweight + (s.weight or 0.0), _workout_date(s))
                for s in rep_sets
            ]
            if totals:
                value, date = max(totals, key=lambda item: item[0])
                records.append(
                    _make_record(
                        "TOTAL_WEIGHT",
                        "Total weight (bodyweight + added)",
                        value,
                        "kg",
                        date,
                    )
                )
    elif is_assisted:
        if weighted:
            value, date = min(weighted, key=lambda item: item[0])
            records.append(
                _make_record(
                    "HEAVIEST_WEIGHT", "Least assistance", value, "kg", date
                )
            )
    elif weighted:
        value, date = max(weighted, key=lambda item: item[0])
        records.append(
            _make_record("HEAVIEST_WEIGHT", "Heaviest weight", value, "kg", date)
        )

    # Estimated 1RM (Epley); skipped for assisted exercises (inverted logic)
    if not is_assisted:
        estimates: list[tuple[float, datetime | None]] = []
        for s in rep_sets:
            reps = s.rep_set.reps
            if reps is None or reps <= 0:
                continue
            if s.weight is None or s.weight <= 0:
                if not (is_bodyweight and bodyweight is not None):
                    continue
            load = s.weight or 0.0
            if is_bodyweight and bodyweight is not None:
                load = bodyweight + load
            est = load * (1 + reps / 30.0) if reps > 1 else load
            estimates.append((est, _workout_date(s)))
        if estimates:
            value, date = max(estimates, key=lambda item: item[0])
            records.append(
                _make_record(
                    "ESTIMATED_1RM", "Estimated 1RM", round(value, 1), "kg", date
                )
            )

    # Most reps per distinct weight
    reps_by_weight: dict[float, tuple[int, datetime | None]] = {}
    for s in rep_sets:
        reps = s.rep_set.reps
        if reps is None or reps <= 0:
            continue
        weight = s.weight if s.weight is not None else 0.0
        current = reps_by_weight.get(weight)
        if current is None or reps > current[0]:
            reps_by_weight[weight] = (reps, _workout_date(s))
    reps_per_weight = [
        schemas.RepsAtWeightRead(weight=weight, reps=reps, date=date)
        for weight, (reps, date) in sorted(reps_by_weight.items())
    ]

    # Most volume in a single set
    volumes: list[tuple[float, datetime | None]] = []
    for s in rep_sets:
        reps = s.rep_set.reps
        if s.weight is None or s.weight <= 0 or reps is None or reps <= 0:
            continue
        volumes.append((s.weight * reps, _workout_date(s)))
    if volumes:
        value, date = max(volumes, key=lambda item: item[0])
        records.append(
            _make_record(
                "MAX_VOLUME", "Most volume (single set)", value, "kg·reps", date
            )
        )

    return schemas.ExercisePRsRead(
        exercise_id=exercise.id, records=records, reps_per_weight=reps_per_weight
    )
