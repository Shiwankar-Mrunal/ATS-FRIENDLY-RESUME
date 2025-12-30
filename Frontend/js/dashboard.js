const tableBody = document.querySelector("#candidateTable tbody");

// Fetch candidates from backend and populate the table
async function loadCandidates() {
  try {
    const response = await fetch("http://127.0.0.1:8000/resume/");
    const candidates = await response.json();

    // Clear existing table rows
    tableBody.innerHTML = "";

    // Sort candidates by score descending
    const ranked = candidates.sort((a, b) => b.score - a.score);

    // Add each candidate as a row
    ranked.forEach(c => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${c.name}</td>
        <td class="score">${c.score}</td>
      `;
      tableBody.appendChild(row);
    });
  } catch (error) {
    console.error("Error fetching candidates:", error);
  }
}

// Load candidates on page load
window.addEventListener("DOMContentLoaded", loadCandidates);
