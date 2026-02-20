1. HTML Structure

2. JavaScript Functionality

3. Role Check

4. Utility Functions

5. Main Function – showATS()

    -   Triggered when the user clicks Calculate ATS Score.

    -   Behavior depends on input:

## A. No custom skills provided

    -   Displays the original scanResult:

    -   ATS score.

    -   -Matched skills.

    -   Missing skills.

    -   Experience years.

    -   Resume link.

## B. Custom skills provided

- Reads and splits Must Have and Nice To Have inputs by commas.

- Uses checkSkills() to determine matched/missing skills for each category.

###  Calculates a new ATS score:
```
ATS Score=Total Matched Skills/Total Skills×100
```

### Dynamically renders:

        ATS score.

        Must-have matched/missing.

        Nice-to-have matched/missing.

        Resume link.

6. Styling

7. Key Features