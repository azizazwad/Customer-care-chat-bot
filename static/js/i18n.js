// English and Bangla UI text, and applying it to the page.

import { els, reducedMotion } from "./dom.js";
import { readStorage, writeStorage } from "./storage.js";

const translations = {
  en: {
    newChat: "New conversation", quickHelp: "Quick help",
    privacyTitle: "Your privacy matters", privacyCopy: "Please don't share passwords or payment details.",
    online: "Support assistant online", headerSubtitle: "AI support assistant · Online",
    welcomeKicker: "Here for you",
    welcomeTitle: 'How can we <span class="gradient-text">help</span><br>you today?',
    welcomeCopy: "Ask us anything. We’re here to make things easier.",
    suggestionProduct: "Product help", suggestionProductCopy: "Features, setup, and compatibility",
    suggestionOrder: "Order question", suggestionOrderCopy: "Delivery, tracking, and returns",
    suggestionHuman: "Talk to a person", suggestionHumanCopy: "Connect with our support team",
    promptProduct: "I need help with a product", promptOrder: "I have a question about an order",
    promptHuman: "I’d like to speak to a person",
    inputPlaceholder: "Message Mikey…",
    inputHint: "<kbd>Enter</kbd> to send · <kbd>Shift</kbd> + <kbd>Enter</kbd> for a new line",
    voice: "Voice", voiceAria: "Speak your message", send: "Send message", stop: "Stop generating",
    aiCaption: "Mikey is an AI assistant and can make mistakes. Messages are sent to Groq to generate replies.",
    themeToggle: "Toggle theme", jumpToLatest: "Latest", botName: "Mikey", you: "You",
    greeting: "Hi there! 👋 Welcome to customer care. How can I help you today?",
    thinking: "Mikey is thinking", copy: "Copy", copied: "Copied", retry: "Try again",
    stopped: "Response stopped", truncated: "This reply was cut short. Ask Mikey to continue.",
    interrupted: "The reply was interrupted. Please try again.",
    voiceUnsupported: "Voice input is not supported in this browser.",
    voiceDenied: "Microphone access was blocked. Please check your browser permissions.",
    failed: "Something went wrong. Please try again.", listening: "Listening… speak now",
    newChatDone: "A fresh conversation is ready.", copyFailed: "Could not copy the reply.",
    notConfigured: "Add GROQ_API_KEY to .env to enable customer-care chat."
  },
  bn: {
    newChat: "নতুন কথোপকথন", quickHelp: "দ্রুত সহায়তা",
    privacyTitle: "আপনার গোপনীয়তা গুরুত্বপূর্ণ", privacyCopy: "পাসওয়ার্ড বা পেমেন্টের তথ্য শেয়ার করবেন না।",
    online: "সাপোর্ট সহকারী অনলাইন", headerSubtitle: "AI সাপোর্ট সহকারী · অনলাইন",
    welcomeKicker: "আপনার পাশে",
    welcomeTitle: 'আজ আপনাকে কীভাবে<br><span class="gradient-text">সাহায্য</span> করতে পারি?',
    welcomeCopy: "যেকোনো প্রশ্ন করুন। আপনার কাজ সহজ করতে আমরা আছি।",
    suggestionProduct: "পণ্য সহায়তা", suggestionProductCopy: "ফিচার, সেটআপ ও সামঞ্জস্যতা",
    suggestionOrder: "অর্ডার সম্পর্কে", suggestionOrderCopy: "ডেলিভারি, ট্র্যাকিং ও রিটার্ন",
    suggestionHuman: "মানুষের সাথে কথা বলুন", suggestionHumanCopy: "আমাদের সাপোর্ট টিমের সাথে যোগাযোগ করুন",
    promptProduct: "একটি পণ্য সম্পর্কে সাহায্য চাই", promptOrder: "একটি অর্ডার সম্পর্কে জানতে চাই",
    promptHuman: "একজন প্রতিনিধির সাথে কথা বলতে চাই",
    inputPlaceholder: "মাইকিকে লিখুন…",
    inputHint: "পাঠাতে <kbd>Enter</kbd> · নতুন লাইনে <kbd>Shift</kbd> + <kbd>Enter</kbd>",
    voice: "কণ্ঠ", voiceAria: "কথা বলে বার্তা দিন", send: "বার্তা পাঠান", stop: "উত্তর থামান",
    aiCaption: "মাইকি একটি AI সহকারী, ভুল হতে পারে। উত্তর তৈরি করতে বার্তা Groq-এ পাঠানো হয়।",
    themeToggle: "থিম পরিবর্তন", jumpToLatest: "সর্বশেষ", botName: "মাইকি", you: "আপনি",
    greeting: "আসসালামু আলাইকুম! 👋 কাস্টমার কেয়ারে স্বাগতম। কীভাবে সাহায্য করতে পারি?",
    thinking: "মাইকি ভাবছে", copy: "কপি", copied: "কপি হয়েছে", retry: "আবার চেষ্টা করুন",
    stopped: "উত্তর থামানো হয়েছে", truncated: "উত্তরটি মাঝপথে শেষ হয়েছে। চালিয়ে যেতে মাইকিকে বলুন।",
    interrupted: "উত্তর মাঝপথে বন্ধ হয়ে গেছে। আবার চেষ্টা করুন।",
    voiceUnsupported: "এই ব্রাউজারে ভয়েস ইনপুট সমর্থিত নয়।",
    voiceDenied: "মাইক্রোফোন ব্যবহারের অনুমতি নেই। ব্রাউজারের সেটিংস দেখুন।",
    failed: "সমস্যা হয়েছে। আবার চেষ্টা করুন।", listening: "শুনছি… এখন বলুন",
    newChatDone: "নতুন কথোপকথন শুরু হয়েছে।", copyFailed: "উত্তরটি কপি করা যায়নি।",
    notConfigured: "কাস্টমার কেয়ার চ্যাট চালু করতে .env ফাইলে GROQ_API_KEY যোগ করুন।"
  }
};

let language = readStorage("mikey-language") === "bn" ? "bn" : "en";

export function getLanguage() { return language; }

export function t(key) { return translations[language][key] ?? translations.en[key] ?? key; }

export function setLanguage(next) {
  language = next === "bn" ? "bn" : "en";
  writeStorage("mikey-language", language);
}

export function applyTranslations(animate = false) {
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t(node.dataset.i18n); });
  document.querySelectorAll("[data-i18n-html]").forEach((node) => { node.innerHTML = t(node.dataset.i18nHtml); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => { node.placeholder = t(node.dataset.i18nPlaceholder); });
  document.querySelectorAll("[data-i18n-aria]").forEach((node) => {
    node.setAttribute("aria-label", t(node.dataset.i18nAria));
    node.title = t(node.dataset.i18nAria);
  });
  els.langSwitch.dataset.active = language;
  els.langSwitch.querySelectorAll("[data-lang]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.lang === language));
  });
  if (animate && !reducedMotion.matches) {
    document.body.classList.remove("lang-swap");
    void document.body.offsetWidth;
    document.body.classList.add("lang-swap");
  }
}
