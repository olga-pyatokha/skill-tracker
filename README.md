# Skill Tracker

Personal skill maps for acro yoga (pole next). `python3 build.py acro` renders
`acro/skills.json` through `template.html` into one page per person
(`acro/olga.html`, `acro/reza.html`) plus a landing `index.html`.

Progress lives in each person's browser. The footer button **Save progress to file**
downloads `acro_progress_<user>.json`; drop it in `acro/` (or Downloads) and rebuild to
bake it into the page.

Live: https://olga-pyatokha.github.io/skill-tracker/
