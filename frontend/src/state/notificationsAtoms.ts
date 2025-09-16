import { atom } from "jotai";
import type { Notification } from "../services/notifications";

export const unreadCountAtom = atom<number>(0);
export const unreadItemsAtom = atom<Notification[]>([]);
export const notifOpenAtom = atom<boolean>(false);
