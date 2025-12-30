const tableBody = document.querySelector("#candidateTable tbody");

getCandidates().forEach(c => {
  const row = document.createElement("tr");
  row.innerHTML = `
    <td>${c.name}</td>
    <td class="score">${c.score}</td>
  `;
  tableBody.appendChild(row);
});
