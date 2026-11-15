// Shared DOM references and small element helpers used by every UI module.

const SVG_NS = "http://www.w3.org/2000/svg";

export const $ = (selector) => document.querySelector(selector);

export const els = {
  mainPanel: $("#main-panel"),
  scroller: $("#scroller"),
  welcome: $("#welcome"),
  thread: $("#messages"),
  form: $("#chat-form"),
  input: $("#message-input"),
  sendButton: $("#send-button"),
  charCount: $("#char-count"),
  jumpButton: $("#jump-button"),
  langSwitch: $("#lang-switch"),
  heroOrb: $("#hero-orb"),
  toast: $("#toast"),
  announcer: $("#announcer"),
  voiceButton: $("#voice-button"),
  themeToggle: $("#theme-toggle"),
  businessName: $("#business-name")
};

export const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
export const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");

export function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

export function icon(name) {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("class", "icon");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS(SVG_NS, "use");
  use.setAttribute("href", `#i-${name}`);
  svg.append(use);
  return svg;
}
