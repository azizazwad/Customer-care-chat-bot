// localStorage access that never throws (it can be blocked in private windows).

export function readStorage(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}

export function writeStorage(key, value) {
  try { localStorage.setItem(key, value); } catch { /* Storage can be unavailable in private windows. */ }
}
