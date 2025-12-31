
// script.js
// Handles resume upload, fetches parsed data from backend, and displays results

console.log("script.js loaded successfully");

async function uploadResume() {
    console.log("Button clicked, function started");

    const fileInput = document.getElementById('resumeFile');
    const resultDiv = document.getElementById('result');

    console.log("File input element:", fileInput);
    console.log("Number of files selected:", fileInput.files.length);

    if (fileInput.files.length === 0) {
        alert("Please upload a resume!");
        return;
    }

    // Show a loading message while processing
    resultDiv.innerHTML = `<p>Uploading and scanning resume...</p>`;

    const formData = new FormData();
    formData.append("resume", fileInput.files[0]);

    try {
        const response = await fetch("http://127.0.0.1:5000/scan", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        console.log("Backend response:", data);

        if (!response.ok || data.error) {
            throw new Error(data.error || "Server returned an error");
        }

        // Display all extracted details
        displayResult(data);

    } catch (error) {
        alert("Error scanning resume. Check backend console.");
        console.error("UploadResume Error:", error);
        resultDiv.innerHTML = "<p style='color:red;'>Error scanning resume. Please try again.</p>";
    }
}

// Display resume details on UI
function displayResult(data) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = ""; // clear previous results
    console.log("Displaying result:", data);

    // Helper function to create a card
    const createCard = (title, content) => {
        const card = document.createElement("div");
        card.className = "result-card";
        card.innerHTML = `<h3>${title}</h3><p>${content || "Not found"}</p>`;
        return card;
    };

    // Add all available fields
    resultDiv.appendChild(createCard("Name", data.name));
    resultDiv.appendChild(createCard("Email", data.email));
    if (data.phone) resultDiv.appendChild(createCard("Phone", data.phone));
    if (data.skills && data.skills.length) resultDiv.appendChild(createCard("Skills", data.skills.join(", ")));
    if (data.education && data.education.length) resultDiv.appendChild(createCard("Education", data.education.join(", ")));
    if (data.experience && data.experience.length) resultDiv.appendChild(createCard("Experience", data.experience.join("\n")));
    if (data.certifications && data.certifications.length) resultDiv.appendChild(createCard("Certifications", data.certifications.join(", ")));

    // Scroll smoothly to the results
    resultDiv.scrollIntoView({ behavior: "smooth" });
}

