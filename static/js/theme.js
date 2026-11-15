// Light and dark themes. Night mode is the default until the visitor picks one.

import { reducedMotion } from "./dom.js";
import { writeStorage } from "./storage.js";

export function currentTheme() { return document.documentElement.dataset.theme === "light" ? "light" : "dark"; }

export function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  document.querySelector('meta[name="theme-color"]').content = theme === "dark" ? "#0e0f16" : "#f6f6fa";
}

export function toggleTheme(event) {
  const next = currentTheme() === "dark" ? "light" : "dark";
  const apply = () => { setTheme(next); writeStorage("mikey-theme-choice", next); };
  if (!document.startViewTransition || reducedMotion.matches) {
    apply();
    return;
  }
  // Reveal the new theme as a circle growing from the toggle button.
  const rect = event.currentTarget.getBoundingClientRect();
  const x = rect.left + rect.width / 2;
  const y = rect.top + rect.height / 2;
  const radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
  document.startViewTransition(apply).ready.then(() => {
    document.documentElement.animate(
      { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] },
      { duration: 650, easing: "cubic-bezier(.22, 1, .36, 1)", pseudoElement: "::view-transition-new(root)" }
    );
  }).catch(() => {});
}
