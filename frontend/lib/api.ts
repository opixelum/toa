const API_BASE_URL = "http://127.0.0.1:8000";

const DEFAULT_USER_ID = 1;

export interface User {
  id: number;
  email: string;
  bodyweight: number | null;
}

export interface Workout {
  id: number;
  user_id: number;
  name: string;
  planned: boolean;
  description: string | null;
  note?: string | null;
  rpe?: number | null;
  creation_date: string;
  mesocycle_id: number | null;
}

export interface Exercise {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  type: "REPS" | "DURATION";
  equipment:
    | "BARBELL"
    | "DUMBBELL"
    | "MACHINE"
    | "BODYWEIGHT"
    | "ASSISTED_BODYWEIGHT";
}

export interface WorkoutExercise {
  id: number;
  workout_id: number;
  exercise_id: number;
  position: number;
  note: string | null;
}

export interface Set {
  id: number;
  workout_id: number;
  exercise_id: number;
  position: number;
  type_: string;
  weight: number | null;
  rpe: number | null;
  rest: number;
}

export interface RepSet extends Set {
  reps: number | null;
}

export interface DurationSet extends Set {
  duration: number;
}

export type WorkoutInput = Omit<Workout, "id" | "creation_date" | "user_id"> & {
  user_id?: number;
};

async function fetchAPI(endpoint: string, options?: RequestInit) {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  if (response.status === 204) {
    return undefined;
  }

  return response.json();
}

export const api = {
  // User
  getUser: (userId: number = DEFAULT_USER_ID) => fetchAPI(`/users/${userId}`),

  updateUser: (userId: number = DEFAULT_USER_ID, data: Partial<User>) =>
    fetchAPI(`/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteUser: (userId: number = DEFAULT_USER_ID) =>
    fetchAPI(`/users/${userId}`, {
      method: "DELETE",
    }),

  // Workouts
  getWorkouts: (userId: number = DEFAULT_USER_ID) =>
    fetchAPI(`/workouts?user_id=${userId}`),

  getWorkout: (workoutId: number) => fetchAPI(`/workouts/${workoutId}`),

  createWorkout: (data: WorkoutInput) =>
    fetchAPI("/workouts", {
      method: "POST",
      body: JSON.stringify({
        ...data,
        user_id: data.user_id ?? DEFAULT_USER_ID,
      }),
    }),

  updateWorkout: (workoutId: number, data: Partial<Workout>) =>
    fetchAPI(`/workouts/${workoutId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteWorkout: (workoutId: number) =>
    fetchAPI(`/workouts/${workoutId}`, {
      method: "DELETE",
    }),

  // Exercises
  getExercises: (userId: number = DEFAULT_USER_ID) =>
    fetchAPI(`/exercises?user_id=${userId}`),

  getExercise: (exerciseId: number) => fetchAPI(`/exercises/${exerciseId}`),

  createExercise: (data: Omit<Exercise, "id" | "user_id">) =>
    fetchAPI("/exercises", {
      method: "POST",
      body: JSON.stringify({ ...data, user_id: DEFAULT_USER_ID }),
    }),

  updateExercise: (exerciseId: number, data: Partial<Exercise>) =>
    fetchAPI(`/exercises/${exerciseId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteExercise: (exerciseId: number) =>
    fetchAPI(`/exercises/${exerciseId}`, {
      method: "DELETE",
    }),

  // Sets
  getSets: (workoutId?: number, exerciseId?: number) => {
    const params = new URLSearchParams();
    if (workoutId) params.append("workout_id", workoutId.toString());
    if (exerciseId) params.append("exercise_id", exerciseId.toString());
    return fetchAPI(`/sets?${params.toString()}`);
  },

  getRepSets: () => fetchAPI("/rep_sets"),

  getDurationSets: () => fetchAPI("/duration_sets"),

  // Create rep/duration sets
  createRepSet: (data: Omit<RepSet, "id" | "set_id">) =>
    fetchAPI("/rep_sets", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  createDurationSet: (data: Omit<DurationSet, "id" | "set_id">) =>
    fetchAPI("/duration_sets", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateRepSet: (setId: number, data: Partial<RepSet>) =>
    fetchAPI(`/rep_sets/${setId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteRepSet: (setId: number) =>
    fetchAPI(`/rep_sets/${setId}`, {
      method: "DELETE",
    }),

  updateDurationSet: (setId: number, data: Partial<DurationSet>) =>
    fetchAPI(`/duration_sets/${setId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteDurationSet: (setId: number) =>
    fetchAPI(`/duration_sets/${setId}`, {
      method: "DELETE",
    }),

  // WorkoutExercises
  getWorkoutExercises: (workoutId: number) =>
    fetchAPI(`/workout_exercises?workout_id=${workoutId}`),

  createWorkoutExercise: (data: Omit<WorkoutExercise, "id">) =>
    fetchAPI("/workout_exercises", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateWorkoutExercise: (id: number, data: Partial<WorkoutExercise>) =>
    fetchAPI(`/workout_exercises/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteWorkoutExercise: (id: number) =>
    fetchAPI(`/workout_exercises/${id}`, {
      method: "DELETE",
    }),
};

export const DEFAULT_USER: User = {
  id: DEFAULT_USER_ID,
  email: "john.doe@example.com",
  bodyweight: 75.0,
};
