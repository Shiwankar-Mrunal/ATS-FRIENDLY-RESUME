// Simulated database
let candidates = JSON.parse(localStorage.getItem("candidates")) || [];

function saveCandidates() {
  localStorage.setItem("candidates", JSON.stringify(candidates));
}

function addCandidate(candidate) {
  candidates.push(candidate);
  saveCandidates();
}

function getCandidates() {
  return candidates;
}
