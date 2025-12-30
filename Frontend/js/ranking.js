const rankingList = document.getElementById("rankingList");

const ranked = getCandidates().sort((a, b) => b.score - a.score);

ranked.forEach(c => {
  const li = document.createElement("li");
  li.textContent = `${c.name} - ${c.score}`;
  rankingList.appendChild(li);
});
