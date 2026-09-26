# Website update workflow

- Work on `main` for website updates. Sync with `origin/main` before making changes.
- After appropriate validation, commit and push the completed changes directly to `origin/main`. The user has authorized this workflow, including the deployment triggered by a push to `main`; no feature branch, pull request, or separate publishing confirmation is needed unless the user requests otherwise.
- Preserve unrelated local changes and untracked files.
- Every new paper or publication metadata/status update must also update the CV through the shared publication source. Regenerate the derived bibliography, JSON Resume, LaTeX fragments, and downloadable PDF; do not stop after updating the website or news.
- Before reporting a publication update complete, verify the paper's CV metadata (title, authors, venue, and year) and confirm that the rebuilt PDF has been deployed.
