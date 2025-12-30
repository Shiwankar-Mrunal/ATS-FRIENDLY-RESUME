document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const fileInput = document.getElementById("resumeFile");
  const jobSkillsInput = document.getElementById("jobSkills").value; // comma-separated skills

  if (fileInput.files.length === 0) {
    alert("Please select a resume file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  // try {
  //   // Parse resume via backend
  //   const parseRes = await fetch("http://127.0.0.1:8000/resume/parse-file", {
  //     method: "POST",
  //     body: formData
  //   });
  //   const parsedData = await parseRes.json();

  //   const name = parsedData.name || "Unknown";
  //   const resumeSkills = parsedData.skills || [];
  //   const jobSkills = jobSkillsInput.split(",").map(s => s.trim()).filter(s => s);
  

    // Add candidate to backend and calculate score
    // const addRes = await fetch("http://127.0.0.1:5500/resume/add", {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json"
    //   },
    //   body: JSON.stringify({
    //     name,
    //     resume_skills: resumeSkills,
    //     job_skills: jobSkills
    //   })
    // });

//     const addResult = await addRes.json();
//     alert(`Resume uploaded successfully! Score: ${addResult.score}`);

//     // Redirect or refresh dashboard
//     window.location.href = "index.html"; // Or call loadCandidates() if on same page
//   } catch (error) {
//     console.error("Error uploading resume:", error);
//     alert("Failed to upload resume. Check console for details.");
//   }
// });


async function uploadResume() {
  try {
    const formData = new FormData();
    formData.append("name", name);
    formData.append("resume_file", document.getElementById("resumeInput").files[0]); // file input element
    formData.append("job_skills", JSON.stringify(jobSkills)); // send as JSON string if needed
    formData.append("resume_skills", JSON.stringify(resumeSkills));

    const addRes = await fetch("http://127.0.0.1:5500/resume/add", {
      method: "POST",
      body: formData, // <-- FormData automatically sets multipart/form-data
    });

    const addResult = await addRes.json();
    alert(`Resume uploaded successfully! Score: ${addResult.score}`);

    // Redirect or refresh dashboard
    window.location.href = "index.html";
  } catch (error) {
    console.error("Error uploading resume:", error);
    alert("Failed to upload resume. Check console for details.");
  }
}

// Example: call the function on a button click
document.getElementById("uploadButton").addEventListener("click", uploadResume);

});