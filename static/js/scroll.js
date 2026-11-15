// Keeps the newest message in view, unless the reader has scrolled up.

import { els, reducedMotion } from "./dom.js";

let stickToBottom = true;

function distanceFromBottom() {
  const { scroller } = els;
  return scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight;
}

export function updateJumpButton() {
  els.jumpButton.classList.toggle("visible", !els.thread.hidden && distanceFromBottom() > 160);
}

export function followScroll(force = false) {
  if (force) stickToBottom = true;
  if (stickToBottom) els.scroller.scrollTop = els.scroller.scrollHeight;
  updateJumpButton();
}

export function scrollToTop() {
  els.scroller.scrollTop = 0;
}

export function initScroll() {
  els.scroller.addEventListener("scroll", () => {
    stickToBottom = distanceFromBottom() < 80;
    updateJumpButton();
  }, { passive: true });
  els.jumpButton.addEventListener("click", () => {
    stickToBottom = true;
    els.scroller.scrollTo({ top: els.scroller.scrollHeight, behavior: reducedMotion.matches ? "auto" : "smooth" });
  });
}
