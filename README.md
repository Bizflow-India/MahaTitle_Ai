# MahaTitle AI – Title Investigation Report Generator

## Project Name (GitHub / Vercel)
- **Repository name:** `maha-title-ai`
- **Human‑readable name:** **MahaTitle AI** – an AI‑powered Title Investigation Report generator.

## Quick Overview (Demo for Mentor)
This repository implements a complete end‑to‑end pipeline that:
1. **Ingests** any PDF agreement placed in `D:\Nilesh` (or uploaded via the web UI).
2. **Extracts** all required legal/property fields using `core/extractor.py`.
3. **Generates** a fully formatted `.docx` Title Investigation Report matching the JM Associates / LIC HFL template.
4. **Provides** a local FastAPI dashboard (`http://localhost:8000`) with drag‑and‑drop upload, parsed metadata view, IGR Smart Filter demo, and download links for every generated report.
5. **Runs** as a daemon task (task‑174) so the server stays alive while you work.

### Demo Script (run in PowerShell)
```powershell
# 1. Start the server (already running as a daemon, but you can restart)
Set-Location D:\Nilesh; python app.py

# 2. Open the UI in a browser
Start-Process "http://localhost:8000"

# 3. Drop a PDF onto the upload zone → you will see parsed data and a "Download Report" button.
```

## Pushing to GitHub
```bash
# Initialise repo (if not already)
git init
git add .
git commit -m "Initial commit – MahaTitle AI"

# Create a GitHub repo (e.g., user/maha-title-ai) and push
git remote add origin https://github.com/<YOUR_USERNAME>/maha-title-ai.git
git branch -M main
git push -u origin main
```

## Deploying to Vercel (Python Serverless)
1. **Install Vercel CLI** (if not present):
   ```
   npm i -g vercel
   ```
2. **Login / Link** to your Vercel account:
   ```
   vercel login
   vercel link
   ```
3. **Add a `vercel.json`** (already in the repo) that tells Vercel to treat `app.py` as a serverless function:
   ```json
   {
     "version": 2,
     "builds": [{ "src": "app.py", "use": "@vercel/python" }],
     "routes": [{ "src": "/(.*)", "dest": "app.py" }]
   }
   ```
4. **Deploy**:
   ```
   vercel --prod
   ```
   Vercel will install the `requirements.txt` dependencies, spin up a serverless endpoint, and give you a public URL (e.g., `https://maha-title-ai.vercel.app`).

> **Note:** Vercel’s serverless functions have a default timeout of 10 seconds. For large PDF batches you may want to limit processing to a single file per request or use background jobs (e.g., Vercel Cron) – the UI already works with a single‑file upload flow.

## Readiness Checklist
- [x] All core modules (`extractor`, `report_generator`, `igr_filter`) are present and unit‑tested.
- [x] FastAPI server runs locally and serves the UI.
- [x] Sample PDF (`Samir Pawar Agreement.pdf`) processes correctly, producing `Title_Investigation_Report_Samir_Pawar.docx`.
- [x] IGR Smart Filter demo works and shows statistics.
- [ ] **Bulk‑processing script** (`process_all_pdfs.py`) added – optional but recommended before a full demo.
- [ ] **Documentation** (`README.md` – this file) finalized.
- [ ] **Vercel deployment** tested – run `vercel --prod` and verify the live URL.

### Verdict for Mentor Presentation
The core functionality (PDF ingestion → DOCX report generation) is fully working and can be demonstrated via the local UI. With the repository pushed to GitHub and a quick Vercel deployment (steps above), you have a live demo URL that showcases the same flow in a cloud‑hosted serverless environment.

**Action items before the presentation:**
1. Run the bulk‑processing script on all client PDFs (if you have more than one).
2. Perform a test deployment on Vercel and confirm the report download works from the public URL.
3. Polish the README (you’re already looking at it) and optionally add a short demo video.

Once these are done, the project is ready to present to your mentor.
