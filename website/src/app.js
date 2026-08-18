// Motion system: slower cinematic boot, typewriter runtime, parallax, ASCII play, scroll reveal, and a desktop-only smooth cursor.
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const boot = document.querySelector("#boot");
const meter = document.querySelector("#boot-meter");
const percent = document.querySelector("#boot-percent");
const bootLine = document.querySelector("#boot-line");
const stage = document.querySelector("#boot-stage");
const bootCheck = document.querySelector("#boot-check");

async function typeInto(element, text, speed = 34) {
  element.textContent = "";
  for (const character of text) { element.textContent += character; await sleep(speed); }
}

async function fillMeter(target, duration) {
  const start = Number(meter.dataset.value || 0); const startTime = performance.now();
  return new Promise((resolve) => {
    const tick = (time) => { const progress = Math.min(1, (time - startTime) / duration); const value = Math.round(start + (target - start) * (1 - Math.pow(1 - progress, 3))); meter.style.width = `${value}%`; percent.textContent = `${String(value).padStart(3, "0")}%`; if (progress < 1) requestAnimationFrame(tick); else { meter.dataset.value = String(target); resolve(); } };
    requestAnimationFrame(tick);
  });
}

async function runBoot() {
  if (reduced) { meter.style.width = "100%"; percent.textContent = "100%"; boot.classList.add("done"); return; }
  const phases = [
    ["A big surprise awaits.", "allocating local runtime", 18, 720],
    ["Preparing your command surface.", "resolving build dependencies", 43, 1050],
    ["Welcome to the future of simple working.", "warming interaction layer", 72, 1300],
    ["BETON is ready when you are.", "local control: online", 100, 950],
  ];
  for (let index = 0; index < phases.length; index += 1) {
    const [copy, status, target, duration] = phases[index];
    bootLine.classList.add("morph-out"); await sleep(160); bootLine.classList.remove("morph-out");
    bootCheck.textContent = `[ 0${index + 1} / 04 ]`; stage.textContent = status;
    await Promise.all([typeInto(bootLine, copy, index === 2 ? 22 : 30), fillMeter(target, duration)]); await sleep(220);
  }
  await sleep(560); boot.classList.add("done");
}
window.addEventListener("load", runBoot, { once: true });

const palette = document.querySelector("#palette"); const object = document.querySelector("#hero-object");
if (!reduced && palette && object) {
  object.addEventListener("pointermove", ({ clientX, clientY }) => { const box = object.getBoundingClientRect(); const x = (clientX - box.left) / box.width - .5; const y = (clientY - box.top) / box.height - .5; palette.style.transform = `rotateX(${-y * 8}deg) rotateY(${x * 10}deg)`; });
  object.addEventListener("pointerleave", () => { palette.style.transform = "rotateX(0) rotateY(0)"; });
}

const commandText = document.querySelector("#command-text"); const rows = [...document.querySelectorAll(".result")];
if (!reduced && commandText && rows.length) {
  const commands = ["open chrome", 'search "electrostatics"', 'note "finish physics DPP"', "timer 25"]; let current = 0;
  setInterval(() => { rows[current].classList.remove("active"); current = (current + 1) % commands.length; commandText.animate([{ opacity: 0, transform: "translateY(6px)", filter: "blur(4px)" }, { opacity: 1, transform: "translateY(0)", filter: "blur(0)" }], { duration: 260, easing: "cubic-bezier(.23,1,.32,1)" }); commandText.textContent = commands[current]; rows[current].classList.add("active"); }, 2600);
}

const ascii = "░▒▓█▄▀▌▐■!?&#$@0123456789*"; const signal = document.querySelector("#ascii-signal");
if (!reduced && signal) setInterval(() => { signal.textContent = `▧ ${[..."SYNC / LOCAL / READY"].map((char, index) => index % 5 === 0 ? ascii[Math.floor(Math.random() * ascii.length)] : char).join("")}`; }, 880);

document.querySelectorAll(".glare").forEach((card) => { card.addEventListener("pointermove", ({ clientX, clientY }) => { const box = card.getBoundingClientRect(); card.style.setProperty("--gx", `${(clientX - box.left) / box.width * 100}%`); card.style.setProperty("--gy", `${(clientY - box.top) / box.height * 100}%`); card.style.setProperty("--go", "1"); }); card.addEventListener("pointerleave", () => card.style.setProperty("--go", "0")); });

document.querySelectorAll("[data-ripple]").forEach((element) => { const original = element.textContent; let frame; element.addEventListener("pointerenter", () => { if (reduced) return; const started = performance.now(); const wave = (now) => { const elapsed = now - started; const radius = elapsed / 760 * original.length; element.textContent = [...original].map((character, index) => character === " " ? character : (Math.abs(index - original.length / 2) < radius && radius - Math.abs(index - original.length / 2) < 3 ? ascii[Math.floor(now / 35 + index) % ascii.length] : character)).join(""); if (elapsed < 760) frame = requestAnimationFrame(wave); else element.textContent = original; }; frame = requestAnimationFrame(wave); }); element.addEventListener("pointerleave", () => { cancelAnimationFrame(frame); element.textContent = original; }); });

const observer = new IntersectionObserver((entries) => entries.forEach((entry) => { if (entry.isIntersecting) { entry.target.classList.add("visible"); observer.unobserve(entry.target); } }), { threshold: .12 }); document.querySelectorAll(".reveal").forEach((item) => observer.observe(item));

const runtime = document.querySelector("#runtime-terminal"); const stream = document.querySelector("#terminal-stream");
async function typeRuntime() {
  const lines = ["$ resolve core dependencies", "✓ typer 0.12.5  available", "✓ rich 13.9.4   available", "✓ local notes   mounted", "$ python -m pip install -e .", "✓ build complete", "$ beton doctor", "● system ready / local control online"];
  stream.textContent = "";
  for (const text of lines) { const row = document.createElement("span"); row.className = "terminal-line"; stream.append(row); for (const char of text) { row.textContent += char; await sleep(reduced ? 0 : 13); } await sleep(reduced ? 0 : 180); }
  await sleep(2400); if (!reduced) typeRuntime();
}
if (runtime && stream) { const runtimeObserver = new IntersectionObserver((entries) => { if (entries.some((entry) => entry.isIntersecting)) { runtimeObserver.disconnect(); typeRuntime(); } }, { threshold: .45 }); runtimeObserver.observe(runtime); }

if (!reduced) {
  const layers = [
    { element: document.querySelector("#hero-object"), depth: .12, render: (layer, offset) => layer.style.setProperty("--parallax-y", `${-offset}px`) },
    { element: document.querySelector(".route-art .slab"), depth: .08, render: (layer, offset) => layer.style.transform = `translate3d(0,${-offset}px,0) rotateX(58deg) rotateZ(-28deg)` },
    { element: document.querySelector(".portrait-frame"), depth: .06, render: (layer, offset) => layer.style.transform = `translate3d(0,${-offset}px,0) rotate(-3.5deg)` },
  ].filter(({ element }) => element); let scrolling = false;
  const updateParallax = () => { const viewport = innerHeight; layers.forEach(({ element, depth, render }) => { const rect = element.getBoundingClientRect(); const offset = (rect.top + rect.height / 2 - viewport / 2) * depth; render(element, offset); }); scrolling = false; };
  addEventListener("scroll", () => { if (!scrolling) { requestAnimationFrame(updateParallax); scrolling = true; } }, { passive: true }); updateParallax();
}

const cursor = document.querySelector("#cursor"); const finePointer = window.matchMedia("(hover:hover) and (pointer:fine)").matches;
if (!reduced && finePointer && cursor) { document.body.classList.add("cursor-on"); let tx = innerWidth / 2, ty = innerHeight / 2, x = tx, y = ty; const move = () => { x += (tx - x) * .18; y += (ty - y) * .18; cursor.style.transform = `translate3d(${x - 14}px,${y - 14}px,0)`; requestAnimationFrame(move); }; addEventListener("pointermove", (event) => { tx = event.clientX; ty = event.clientY; cursor.classList.add("live"); }); document.querySelectorAll("a,.glare,#hero-object,.portrait-frame").forEach((item) => { item.addEventListener("pointerenter", () => cursor.classList.add("hover")); item.addEventListener("pointerleave", () => cursor.classList.remove("hover")); }); move(); }
