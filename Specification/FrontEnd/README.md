#  1.5 "***How FrontEnd will work***"
## 1. Global Variables

```
window.selectedRole = "";
```

## 2. Select Role Function

- Updates the selected role.

```
function selectRole(role) {
    window.selectedRole = role;

    const resultDiv = document.getElementById("result");
    if (resultDiv) {
        resultDiv.innerHTML = `
            <div class="result-card">
                <h3 style="justify-content: center; text-align: center; color: #240680; font-size: 40px; font-weight: bold;">Selected Role</h3>
                <p style="color: #c4380d; font-size: 30px; font-weight: bold; justify-content: center; text-align: center;">${role}</p>
            </div>
        `;
    }
}
```

## 3. uploadResume function

### Get the file input element:

```
const fileInput = document.getElementById("resumeFile");
```

### Validate role selection:
```
if (!window.selectedRole) { alert("Please select a role first."); return; }
```

### Validate file upload:
```
if (!fileInput || fileInput.files.length === 0) { alert("Please upload a resume."); return; }
```
### Prepare the form data for sending:
```
const formData = new FormData();
formData.append("resume", fileInput.files[0]);
formData.append("user_type", userType);
formData.append("selected_role", window.selectedRole);
```
Creates a FormData object that holds:

- the uploaded file (resume),

- the user type (job_seeker or hiring_manager),

- the selected role

### Determine API URL
```
const API_BASE_URL =
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:5000"
        : "https://ats-friendly-resume.onrender.com";
```

### Send the request to the server:
```
const response = await fetch(`${API_BASE_URL}/scan`, { method: "POST", body: formData });
const data = await response.json();
if (!response.ok) throw new Error(data.error || "Server error");

```
### Save the scan results and role in session storage:
```
sessionStorage.setItem("scanResult", JSON.stringify(data));
sessionStorage.setItem("selectedRole", window.selectedRole);
```
### Redirect the user based on type:

```
if (userType === "job_seeker") window.location.href = "/job_seeker_result";
else if (userType === "hiring_manager") window.location.href = "/hiring_manager_result";

```
### Handle errors:

catch (error) { console.error("Scan Error:", error); ... }

## 4. loadPreviousResumes function

### Get the dropdown element

```
const dropdown = document.getElementById("previousResumeDropdown");
if (!dropdown) return; // skip if not present
```
### Determine the API base URL
```
const API_BASE_URL =
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:5000"
        : "https://ats-friendly-resume.onrender.com";
```
### Fetch previously uploaded resumes
```
const response = await fetch(`${API_BASE_URL}/get_uploaded_resumes`);
const files = await response.json();
```

### Populate the dropdown
```
dropdown.innerHTML = `<option value="">Select Previous Resume</option>`;
```

- Clears any existing options in the dropdown.

- Adds a default first option prompting the user to select a file.

```
files.forEach(file => {
    const option = document.createElement("option");
    option.value = file;
    option.textContent = file;
    dropdown.appendChild(option);
});
```
### Error handling
```
catch (error) {
    console.error("Error loading previous resumes:", error);
}
```


## scanPreviousResume function:

### Get the selected file
```
const filename = document.getElementById("previousResumeDropdown").value;
```
### Validate the selected role
```
if (!window.selectedRole) {
    alert("Please select a role first.");
    return;
}
```
### Validate that a resume is selected
```
if (!filename) {
    alert("Please select a resume.");
    return;
}
```
### Determine the API base URL
```
const API_BASE_URL =
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:5000"
        : "https://ats-friendly-resume.onrender.com";
```

### Send a POST request to scan the selected file`
```
const response = await fetch(`${API_BASE_URL}/scan_existing_resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        filename: filename,
        selected_role: window.selectedRole
    })
});
```

### Handle the server response
```
const data = await response.json();
if (!response.ok) throw new Error(data.error || "Server error");
```
### Save results and redirect
```
sessionStorage.setItem("scanResult", JSON.stringify(data));
sessionStorage.setItem("selectedRole", window.selectedRole);
window.location.href = "/hiring_manager_result";
```
### Handle errors gracefully
```
catch (error) {
    console.error("Error scanning previous resume:", error);
    const resultDiv = document.getElementById("result");
    if (resultDiv) resultDiv.innerHTML = `<p style="color:red;">Error scanning resume</p>`;
}
``