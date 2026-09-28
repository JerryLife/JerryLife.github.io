# Website update workflow

- Work on `main` for website updates. Sync with `origin/main` before making changes.
- Before every deployment, validate the changes, generate a local website preview, and present it to the user for review. Wait for the user's explicit approval of that preview before pushing to `origin/main` or triggering any deployment.
- After the user approves the local preview, commit and push the approved changes directly to `origin/main`; no feature branch or pull request is needed unless the user requests otherwise. If the website changes after approval, regenerate the local preview and obtain approval again before deployment.
- Preserve unrelated local changes and untracked files.
- Every new paper or publication metadata/status update must also update the CV through the shared publication source. Regenerate the derived bibliography, JSON Resume, LaTeX fragments, and downloadable PDF; do not stop after updating the website or news.
- Before reporting a publication update complete, verify the paper's CV metadata (title, authors, venue, and year) and confirm that the rebuilt PDF has been deployed.
