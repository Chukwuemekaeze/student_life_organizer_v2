// src/state/tasksAtoms.ts
import { atom } from "jotai";
import type { Task } from "../services/tasks";

export type TaskFilters = {
  status: "all" | "todo" | "in_progress" | "done";
  q: string;
  due_before?: string;
  due_after?: string;
};

export const tasksAtom = atom<Task[]>([]);
export const tasksLoadingAtom = atom<boolean>(false);
export const tasksTotalAtom = atom<number>(0);
export const taskFiltersAtom = atom<TaskFilters>({ status: "all", q: "" });

