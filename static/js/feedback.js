// Toast notifications and click ripples.

import { element, els, reducedMotion } from "./dom.js";

let toastTimer;

export function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.add("visible");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => els.toast.classList.remove("visible"), 3400);
}

export function addRipple(event) {
  const host = event.currentTarget;
  if (reducedMotion.matches || host.disabled) return;
  const rect = host.getBoundingClientRect();
  const ripple = element("span", "ripple");
  ripple.style.left = `${event.clientX - rect.left}px`;
  ripple.style.top = `${event.clientY - rect.top}px`;
  host.append(ripple);
  ripple.addEventListener("animationend", () => ripple.remove());
}
