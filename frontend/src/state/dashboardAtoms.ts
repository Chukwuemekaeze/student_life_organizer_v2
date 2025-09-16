// src/state/dashboardAtoms.ts
import { atom } from "jotai";
import type { Metrics, SeriesPayload, Streaks, Summary, ReflectionResult } from "../services/dashboard";

export const metricsAtom = atom<Metrics | null>(null);
export const metricsLoadingAtom = atom<boolean>(false);

// New in Phase 2
export const seriesAtom = atom<SeriesPayload | null>(null);
export const seriesLoadingAtom = atom<boolean>(false);

export const streaksAtom = atom<Streaks | null>(null);
export const streaksLoadingAtom = atom<boolean>(false);

export const summaryAtom = atom<Summary | null>(null);
export const summaryLoadingAtom = atom<boolean>(false);

export const reflectionAtom = atom<ReflectionResult | null>(null);
export const reflectionLoadingAtom = atom<boolean>(false);
