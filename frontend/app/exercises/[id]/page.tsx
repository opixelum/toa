"use client";

import { Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api, type Exercise, type ExercisePRs } from "@/lib/api";

export default function ExercisePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const router = useRouter();
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [type, setType] = useState<"REPS" | "DURATION">("REPS");
  const [equipment, setEquipment] = useState<
    | "BARBELL"
    | "DUMBBELL"
    | "MACHINE"
    | "BODYWEIGHT"
    | "ASSISTED_BODYWEIGHT"
    | null
  >(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [prs, setPrs] = useState<ExercisePRs | null>(null);

  useEffect(() => {
    async function loadExercise() {
      try {
        const { id } = await params;
        const exerciseId = Number.parseInt(id, 10);
        const [exerciseData, prsData] = await Promise.all([
          api.getExercise(exerciseId),
          api.getExercisePRs(exerciseId),
        ]);
        setExercise(exerciseData);
        setPrs(prsData);
        setName(exerciseData.name);
        setDescription(exerciseData.description || "");
        setType(exerciseData.type as "REPS" | "DURATION");
        setEquipment(exerciseData.equipment);
      } catch (error) {
        console.error("Error loading exercise:", error);
      } finally {
        setLoading(false);
      }
    }
    loadExercise();
  }, [params]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!exercise || !name.trim() || !equipment) return;

    setSaving(true);
    try {
      await api.updateExercise(exercise.id, {
        name,
        description: description || null,
        type,
        equipment,
      });
      router.push("/exercises");
    } catch (error) {
      console.error("Error updating exercise:", error);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!exercise) return;
    if (!confirm("Are you sure you want to delete this exercise?")) return;

    setDeleting(true);
    try {
      await api.deleteExercise(exercise.id);
      router.push("/exercises");
    } catch (error) {
      console.error("Error deleting exercise:", error);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return <div className="container mx-auto p-6">Loading...</div>;
  }

  if (!exercise) {
    return <div className="container mx-auto p-6">Exercise not found</div>;
  }

  return (
    <div className="container mx-auto p-6">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Edit Exercise</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSave} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Exercise name"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Input
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Exercise description"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="type">Type</Label>
              <Select
                value={type}
                onValueChange={(value) => {
                  if (value === "REPS" || value === "DURATION") {
                    setType(value);
                  }
                }}
              >
                <SelectTrigger id="type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="REPS">Rep-based</SelectItem>
                  <SelectItem value="DURATION">Duration-based</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="equipment">Equipment</Label>
              <Select
                value={equipment ?? ""}
                onValueChange={(value) => {
                  if (value) {
                    setEquipment(
                      value as
                        | "BARBELL"
                        | "DUMBBELL"
                        | "MACHINE"
                        | "BODYWEIGHT"
                        | "ASSISTED_BODYWEIGHT",
                    );
                  }
                }}
              >
                <SelectTrigger id="equipment">
                  <SelectValue placeholder="Select equipment" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="BARBELL">Barbell</SelectItem>
                  <SelectItem value="DUMBBELL">Dumbbell</SelectItem>
                  <SelectItem value="MACHINE">Machine</SelectItem>
                  <SelectItem value="BODYWEIGHT">Bodyweight</SelectItem>
                  <SelectItem value="ASSISTED_BODYWEIGHT">
                    Assisted Bodyweight
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex gap-2 justify-between">
              <Button
                type="button"
                size="icon"
                variant="destructive"
                className="border-destructive/40"
                onClick={handleDelete}
                disabled={saving || deleting}
                title="Delete exercise"
              >
                <Trash2 className="size-4" />
              </Button>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push("/exercises")}
                  disabled={saving || deleting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={saving || deleting || !name.trim() || !equipment}
                >
                  {saving ? "Saving..." : "Save"}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="max-w-2xl mx-auto mt-6">
        <CardHeader>
          <CardTitle>Personal Records</CardTitle>
        </CardHeader>
        <CardContent>
          {prs && (prs.records.length > 0 || prs.reps_per_weight.length > 0) ? (
            <div className="space-y-4">
              {prs.records.map((record) => (
                <div
                  key={record.type}
                  className="flex items-center justify-between border-b pb-2"
                >
                  <div>
                    <div className="font-medium">{record.label}</div>
                    {record.date && (
                      <div className="text-xs text-muted-foreground">
                        {new Date(record.date).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                  <div className="font-semibold">
                    {record.value} {record.unit}
                  </div>
                </div>
              ))}
              {prs.reps_per_weight.length > 0 && (
                <div>
                  <div className="font-medium mb-2">Most reps per weight</div>
                  <div className="space-y-1">
                    {prs.reps_per_weight.map((rw) => (
                      <div
                        key={rw.weight}
                        className="flex items-center justify-between text-sm"
                      >
                        <span>{rw.weight} kg</span>
                        <span className="flex items-center gap-2">
                          <span className="font-semibold">{rw.reps} reps</span>
                          {rw.date && (
                            <span className="text-xs text-muted-foreground">
                              {new Date(rw.date).toLocaleDateString()}
                            </span>
                          )}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">
              No personal records yet — log some workouts to see them here.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
