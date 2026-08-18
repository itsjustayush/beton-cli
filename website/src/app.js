// Static interaction layer: browser-native loader, CSS 3D palette, glare, ASCII ripple, viewport reveals, and a desktop-only smooth cursor.
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const boot = document.querySelector("#boot");
const meter = document.querySelector("#boot-meter");
const percent = document.querySelector("#boot-percent");
const line = document.querySelector("#boot-line");

window.addEventListener("load", () => {
  if (reduced) { meter.style.width = "100%"; percent.textContent = "100%"; boot.classList.add("done"); return; }
  const phrases = ["A big surprise awaits.", "Welcome to the future.", "Simple working, engaged."];
  let value = 0; let phrase = 0;
  const interval = setInterval(() => {
    value = Math.min(100, value + Math.max(2, Math.round((100 - value) * .085)));
    meter.style.width = `${value}%`; percent.textContent = `${String(value).padStart(3, "0")}%`;
    if (value > 30 && phrase === 0) { phrase = 1; line.textContent = phrases[phrase]; }
    if (value > 67 && phrase === 1) { phrase = 2; line.textContent = phrases[phrase]; }
    if (value === 100) { clearInterval(interval); setTimeout(() => boot.classList.add("done"), 220); }
  }, 52);
}, { once: true });

const palette = document.querySelector("#palette"); const object = document.querySelector("#hero-object");
if (!reduced && palette && object) {
  object.addEventListener("pointermove", ({ clientX, clientY }) => { const box = object.getBoundingClientRect(); const x = (clientX - box.left) / box.width - .5; const y = (clientY - box.top) / box.height - .5; palette.style.transform = `rotateX(${-y * 8}deg) rotateY(${x * 10}deg)`; });
  object.addEventListener("pointerleave", () => palette.style.transform = "rotateX(0) rotateY(0)");
}

const commandText = document.querySelector("#command-text"); const rows = [...document.querySelectorAll(".result")];
if (!reduced && commandText && rows.length) {
  const commands = ["open chrome", 'search "electrostatics"', 'note "finish physics DPP"', "timer 25"]; let current = 0;
  setInterval(() => { rows[current].classList.remove("active"); current = (current + 1) % commands.length; commandText.animate([{ opacity: 0, transform: "translateY(6px)", filter: "blur(4px)" }, { opacity: 1, transform: "translateY(0)", filter: "blur(0)" }], { duration: 230, easing: "cubic-bezier(.23,1,.32,1)" }); commandText.textContent = commands[current]; rows[current].classList.add("active"); }, 2400);
}

document.querySelectorAll(".glare").forEach((card) => { card.addEventListener("pointermove", ({ clientX, clientY }) => { const box = card.getBoundingClientRect(); card.style.setProperty("--gx", `${(clientX - box.left) / box.width * 100}%`); card.style.setProperty("--gy", `${(clientY - box.top) / box.height * 100}%`); card.style.setProperty("--go", "1"); }); card.addEventListener("pointerleave", () => card.style.setProperty("--go", "0")); });

const characters = ".,·-─~+:;=*π┐┌┘┴┬╗╔╝╚╬╠╣╩╦║░▒▓█▄▀▌▐■!?&#$@0123456789*";
document.querySelectorAll("[data-ripple]").forEach((element) => { const original = element.textContent; let frame; element.addEventListener("pointerenter", () => { if (reduced) return; const started = performance.now(); const wave = (now) => { const elapsed = now - started; const radius = elapsed / 760 * original.length; element.textContent = [...original].map((character, index) => character === " " ? character : (Math.abs(index - original.length / 2) < radius && radius - Math.abs(index - original.length / 2) < 3 ? characters[Math.floor(now / 35 + index) % characters.length] : character)).join(""); if (elapsed < 760) frame = requestAnimationFrame(wave); else element.textContent = original; }; frame = requestAnimationFrame(wave); }); element.addEventListener("pointerleave", () => { cancelAnimationFrame(frame); element.textContent = original; }); });

const observer = new IntersectionObserver((entries) => entries.forEach((entry) => { if (entry.isIntersecting) { entry.target.classList.add("visible"); observer.unobserve(entry.target); } }), { threshold: .12 }); document.querySelectorAll(".reveal").forEach((item) => observer.observe(item));

const cursor = document.querySelector("#cursor"); const finePointer = window.matchMedia("(hover:hover) and (pointer:fine)").matches;
if (!reduced && finePointer && cursor) { document.body.classList.add("cursor-on"); let tx = innerWidth / 2, ty = innerHeight / 2, x = tx, y = ty; const move = () => { x += (tx - x) * .18; y += (ty - y) * .18; cursor.style.transform = `translate3d(${x - 14}px,${y - 14}px,0)`; requestAnimationFrame(move); }; addEventListener("pointermove", (event) => { tx = event.clientX; ty = event.clientY; cursor.classList.add("live"); }); document.querySelectorAll("a,.glare,#hero-object").forEach((item) => { item.addEventListener("pointerenter", () => cursor.classList.add("hover")); item.addEventListener("pointerleave", () => cursor.classList.remove("hover")); }); move(); }
