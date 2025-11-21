document.addEventListener("DOMContentLoaded", () => {


  // --- 1) ALWAYS apply the year-length limit to ALL date inputs ---
  const dateInputs = Array.from(document.querySelectorAll('input[type="date"]'));


  const limitYearLength = (input) => {
    input.addEventListener("input", () => {
      const v = input.value;
      if (v && v.split("-")[0].length > 4) {
        const parts = v.split("-");
        parts[0] = parts[0].slice(0, 4);
        input.value = parts.join("-");
      }
    });
  };


  dateInputs.forEach(limitYearLength);




  // --- 2) INTERVAL/DATE logic only if label == "Intervalo" ---
  const intervalLabel = Array.from(document.querySelectorAll("label"))
    .find(label => label.textContent.trim() === "Intervalo");


  if (!intervalLabel) return;


  const selectId = intervalLabel.getAttribute("for");
  const selectInterval = document.getElementById(selectId);


  if (!selectInterval || dateInputs.length < 2) return;


  const [inputStart, inputEnd] = dateInputs;


  const formatDate = (d) => d.toISOString().split("T")[0];


  const toggleDateInputs = (readonly) => {
    inputStart.readOnly = readonly;
    inputEnd.readOnly = readonly;
  };


  const updateDates = () => {
    const value = selectInterval.value;


    if (value === "custom") {
      toggleDateInputs(false);
      return;
    }


    const days = parseInt(value, 10);
    if (Number.isNaN(days)) {
      toggleDateInputs(false);
      return;
    }


    const today = new Date();
    const start = new Date(today);
    start.setDate(today.getDate() - days);


    inputStart.value = formatDate(start);
    inputEnd.value = formatDate(today);
    toggleDateInputs(true);
  };




  // ---------- FIX: allow switching to "custom" even when inputs are readOnly ----------
  const forceCustom = (ev) => {
    if (selectInterval.value !== "custom") {
      selectInterval.value = "custom";
      toggleDateInputs(false);
      selectInterval.dispatchEvent(new Event("change", { bubbles: true }));
      ev.target.focus();
    }
  };


  // Switch to custom on user interaction
  ["pointerdown", "mousedown", "touchstart", "focus"].forEach(evt => {
    inputStart.addEventListener(evt, forceCustom, { passive: true });
    inputEnd.addEventListener(evt, forceCustom, { passive: true });
  });
  // -------------------------------------------------------------------------------




  // Manual edit fallback
  const onManualEdit = () => {
    if (selectInterval.value !== "custom") {
      selectInterval.value = "custom";
      toggleDateInputs(false);
    }
  };


  inputStart.addEventListener("input", onManualEdit);
  inputEnd.addEventListener("input", onManualEdit);


  selectInterval.addEventListener("change", updateDates);


  updateDates();
});
