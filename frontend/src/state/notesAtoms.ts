// src/state/notesAtoms.ts
import { atom } from "jotai";
import type { NoteItem } from "../services/notes";

export const notesAtom = atom<NoteItem[] | null>(null);
export const notesLoadingAtom = atom<boolean>(false);
export const notesConnectedAtom = atom<boolean>(false);


