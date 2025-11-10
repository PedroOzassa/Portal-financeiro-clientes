document.addEventListener("DOMContentLoaded", () => {
  const selectInterval = document.querySelector("select.form-select");
  const dateInputs = document.querySelectorAll('input[type="date"]');
  if (!selectInterval || dateInputs.length < 2) return;

  const [inputStart, inputEnd] = dateInputs;

  // Format date to YYYY-MM-DD for <input type="date">
  const formatDate = (d) => d.toISOString().split("T")[0];

  // Enable/disable date inputs
  const toggleDateInputs = (readonly) => {
    inputStart.readOnly = readonly;
    inputEnd.readOnly = readonly;
  };
  
  // On interval change
  selectInterval.addEventListener("change", () => {
    const value = selectInterval.value;
    if (value === "custom") {
      toggleDateInputs(false);
      return;
    }

    const today = new Date();
    const start = new Date(today);
    start.setDate(today.getDate() - parseInt(value, 10));

    inputStart.value = formatDate(start);
    inputEnd.value = formatDate(today);
    toggleDateInputs(true);
  });

  // When manually editing either date → set interval to "custom"
  [inputStart, inputEnd].forEach((input) => {
    input.addEventListener("input", () => {
      selectInterval.value = "custom";
      toggleDateInputs(false);
    });
  });
});
