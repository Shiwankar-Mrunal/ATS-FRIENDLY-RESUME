# Explaining job seeker html

1. HTML Document Setup

2. Link to CSS
3. Page Heading

4. Result Container
5. JavaScript for Dynamic Content
    ```
    const data = JSON.parse(sessionStorage.getItem("scanResult") || "{}");
    const selectedRole = sessionStorage.getItem("selectedRole") || "";
    ```
6. No Data Handling
    ```
    if (!data || Object.keys(data).length === 0) {
        resultDiv.innerHTML = "<p>No scan data found. Please go back and scan your resume.</p>";
    }
    ```
7. Display Selected Role
    ```
    <p>${selectedRole}</p>

    ```
8. Display ATS Score
    ```
    <p>${data.ats_score || 0}%</p>
    ```
9. Provide Feedback

    -   Feedback changes based on ATS score:

    -   ≥ 90 → “Excellent match”

    -   70–89 → “Good profile, but you can improve…”

    -   40–69 → “Resume needs improvement”

    -   < 40 → “Resume is not suitable”

10. List Missing Skills

11. Render Dynamic HTML