const rankingList = document.getElementById("rankingList");

// Fetch candidates from backend
async function loadRanking() {
  try {
    const response = await fetch("http://127.0.0.1:8000/resume/");
    const candidates = await response.json();

    // Clear existing list
    rankingList.innerHTML = "";

    // Sort by score descending
    const ranked = candidates.sort((a, b) => b.score - a.score);

    // Add each candidate to the list
    ranked.forEach(c => {
      const li = document.createElement("li");
      li.textContent = `${c.name} - ${c.score} (${c.matched_skills.join(", ")})`;
      rankingList.appendChild(li);
    });
  } catch (error) {
    console.error("Error fetching ranking:", error);
  }
}

// Load ranking on page load
window.addEventListener("DOMContentLoaded", loadRanking);
