// script.js — Enhances user interaction in the AI Study Planner

document.addEventListener("DOMContentLoaded", function() {
  const form = document.querySelector("form");
  const subjectInput = document.querySelector("input[name='subjects']");
  const diffInput = document.querySelector("input[name='difficulty']");
  const scoreInput = document.querySelector("input[name='scores']");
  const morning = document.querySelector("input[name='morning']");
  const afternoon = document.querySelector("input[name='afternoon']");
  const night = document.querySelector("input[name='night']");
  
  // 🔹 Auto-balance focus suggestion
  function updateFocusSummary() {
    const summary = document.getElementById("focus_summary");
    if (summary) {
      summary.innerText = `Focus Preference → Morning: ${morning.value}, Afternoon: ${afternoon.value}, Night: ${night.value}`;
    }
  }

  morning.addEventListener("input", updateFocusSummary);
  afternoon.addEventListener("input", updateFocusSummary);
  night.addEventListener("input", updateFocusSummary);

  // 🔹 Example Helper — auto-fill dummy data
  document.getElementById("fillExample")?.addEventListener("click", function() {
    subjectInput.value = "Math, Science, English";
    diffInput.value = "8,6,7";
    scoreInput.value = "70,85,65";
  });

  // 🔹 Simple input validation before submit
  form.addEventListener("submit", function(e) {
    const subjects = subjectInput.value.split(",").map(s => s.trim());
    const diffs = diffInput.value.split(",").map(Number);
    const scores = scoreInput.value.split(",").map(Number);

    if (subjects.length !== diffs.length || diffs.length !== scores.length) {
      e.preventDefault();
      alert("❗ Subjects, difficulties, and scores must have the same count!");
      return;
    }

    if (diffs.some(d => d < 1 || d > 10) || scores.some(s => s < 0 || s > 100)) {
      e.preventDefault();
      alert("⚠️ Difficulty must be 1–10 and Scores must be 0–100.");
    }
  });
});
