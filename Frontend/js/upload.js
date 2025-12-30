document.getElementById("uploadForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const name = document.getElementById("name").value;
  const jobDesc = document.getElementById("jobDesc").value;

  // Fake ATS score
  const score = Math.floor(Math.random() * 40) + 60;

  addCandidate({ name, jobDesc, score });

  alert("Resume uploaded successfully!");
  window.location.href = "index.html";
});
