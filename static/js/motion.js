// Ambient motion: background parallax, the mascot's gaze, and card spotlights.

import { els, finePointer, reducedMotion } from "./dom.js";

let pointerFrame = 0;
let lastPointer = null;
let lastPointerMove = 0;

function setGaze(lookX, lookY, tiltX, tiltY) {
  const orb = els.heroOrb;
  orb.style.setProperty("--look-x", `${lookX.toFixed(2)}px`);
  orb.style.setProperty("--look-y", `${lookY.toFixed(2)}px`);
  orb.style.setProperty("--tilt-x", `${tiltX.toFixed(2)}deg`);
  orb.style.setProperty("--tilt-y", `${tiltY.toFixed(2)}deg`);
}

function lookAt(x, y) {
  const rect = els.heroOrb.getBoundingClientRect();
  const dx = Math.max(-1, Math.min(1, (x - (rect.left + rect.width / 2)) / (innerWidth / 2)));
  const dy = Math.max(-1, Math.min(1, (y - (rect.top + rect.height / 2)) / (innerHeight / 2)));
  setGaze(dx * 6, dy * 5, -dy * 14, dx * 16);
}

function onPointerFrame() {
  pointerFrame = 0;
  if (!lastPointer) return;
  const { x, y } = lastPointer;
  document.documentElement.style.setProperty("--px", ((x / innerWidth) * 2 - 1).toFixed(3));
  document.documentElement.style.setProperty("--py", ((y / innerHeight) * 2 - 1).toFixed(3));
  if (!els.welcome.hidden && document.activeElement !== els.input) lookAt(x, y);
}

function glanceAtComposer() {
  if (reducedMotion.matches) return;
  // Glance down at the message box while the customer types.
  setGaze(0, 5, -12, 0);
}

function setUpCardSpotlights() {
  document.querySelectorAll(".suggestion").forEach((card) => {
    card.addEventListener("pointermove", (event) => {
      if (reducedMotion.matches || !finePointer.matches) return;
      const rect = card.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width;
      const y = (event.clientY - rect.top) / rect.height;
      card.style.setProperty("--mx", `${(x * 100).toFixed(1)}%`);
      card.style.setProperty("--my", `${(y * 100).toFixed(1)}%`);
      card.style.setProperty("--ry", `${((x - 0.5) * 12).toFixed(2)}deg`);
      card.style.setProperty("--rx", `${((0.5 - y) * 12).toFixed(2)}deg`);
    });
    card.addEventListener("pointerleave", () => {
      card.style.setProperty("--rx", "0deg");
      card.style.setProperty("--ry", "0deg");
    });
  });
}

export function setMascotHappy(happy) {
  els.heroOrb.classList.toggle("is-happy", happy);
}

export function initMotion() {
  window.addEventListener("pointermove", (event) => {
    if (reducedMotion.matches || event.pointerType !== "mouse") return;
    lastPointer = { x: event.clientX, y: event.clientY };
    lastPointerMove = performance.now();
    if (!pointerFrame) pointerFrame = requestAnimationFrame(onPointerFrame);
  }, { passive: true });

  // When the visitor is idle, Mikey glances around on its own.
  window.setInterval(() => {
    if (reducedMotion.matches || els.welcome.hidden || document.hidden || document.activeElement === els.input) return;
    if (performance.now() - lastPointerMove < 3500) return;
    const rect = els.heroOrb.getBoundingClientRect();
    const angle = Math.random() * Math.PI * 2;
    const reach = 0.25 + Math.random() * 0.5;
    lookAt(rect.left + rect.width / 2 + Math.cos(angle) * innerWidth * reach,
      rect.top + rect.height / 2 + Math.sin(angle) * innerHeight * reach);
  }, 2600);

  els.input.addEventListener("focus", glanceAtComposer);
  setUpCardSpotlights();
}
