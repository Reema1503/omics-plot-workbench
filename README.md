# Omics Plot Workbench

A Python dashboard for interpreting existing PCA and heatmap images. It does not calculate PCA or heatmaps from raw data.

## Windows / VS Code: first run

1. Extract this ZIP and open the `omics_plot_workbench` folder in VS Code.
2. Open Terminal → New Terminal (PowerShell).
3. Run these commands one at a time, from that folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the Local URL shown in the terminal, normally http://localhost:8501.
If your histology dashboard already uses 8501, run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
```

Open http://localhost:8502 in that case. Keep the terminal running while using the dashboard. Ctrl+C stops it.

If `py` is unavailable, use your working Python interpreter instead of `py` for the first command.

## How to use

1. Enter study details; leave unknown fields blank.
2. Upload up to six PNG/JPEG/WEBP images; label each PCA/Heatmap/Other and add label corrections.
3. Choose a mode in the sidebar:
   - **ChatGPT prompt:** no API key needed. Copy/download the generated prompt and upload the same images to ChatGPT. Paste the answer into the report editor.
   - **Automatic AI:** choose Google Gemini or OpenAI. For Gemini, get your own key at https://aistudio.google.com/apikey and enter it in the Gemini key field. The default is `gemini-2.5-flash` (editable). Free-tier availability and quotas depend on your account; billing-enabled projects may be charged. For OpenAI, enter an OpenAI key (default model `gpt-4.1`). Click Interpret my figures. Your report appears inside the dashboard.
4. Review and edit the interpretation. Download a Markdown report or a ZIP containing the report, figures, study details and prompt.

API keys are excluded from downloads and are not written to disk by the app. Each visitor enters their own key; the app does not load server-side keys. Figures and study details are sent only to the provider you select, when you click Interpret. Provider data-handling terms apply; free-tier terms may differ by region and billing status. Use the simulated examples for initial testing. Sessions are kept in memory; download work before closing.

## Update an existing GitHub / Render deployment

1. Extract `omics_plot_workbench_gemini.zip`.
2. Open your GitHub repository. Choose Add file → Upload files.
3. Upload the extracted `app.py`, `analysis.py`, `requirements.txt`, and `README.md` directly at the repository root, replacing the old files. Commit changes.
4. If Render auto-deploy is enabled, wait for it to redeploy. Otherwise deploy the latest commit manually.
5. Open the dashboard and check that it shows Version 1.1 · Gemini + OpenAI.
6. Choose Automatic AI interpretation → Google Gemini. Paste your Gemini key, upload plots, and click Interpret my figures.

Render commands remain:
- Build: `pip install -r requirements.txt`
- Start: `python -m streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`

For local updates, replace the same files and restart Streamlit. No new dependency is needed.

## Gemini troubleshooting

- Quota/rate limit: wait and retry; check your project allowance in Google AI Studio. The app does not automatically retry or switch to a paid service.
- Model unavailable: choose an image-capable model available for your account and enter its model ID.
- Incomplete or blocked report: the app keeps your existing report; try fewer figures or review the context.
- Large request: use fewer/smaller PNGs. Gemini requests are limited here to 19 MB after encoding; per-image upload limits also apply.

Validation: nine offline tests passed, including provider routing, image payloads, blocked/incomplete responses, quota errors, and keeping the key out of the request URL/body. A live Gemini call requires your key and has not been tested. Streamlit UI execution was unavailable in the build environment.

Official Gemini references:
- https://ai.google.dev/api/generate-content
- https://ai.google.dev/gemini-api/docs/pricing


The interpretation prompt asks for observations, provisional explanations, a combined interpretation, up to three next steps, a Results paragraph and individual captions. It prohibits invented details and significance/causation claims from figures alone. AI may still misread a figure; review every sample label, value and biological claim.

PDF and TIFF inputs are not supported; export those plots as PNG. This app cannot automatically retrieve plots from your previous chats. Upload them again in the dashboard.

## Verification

The included standard-library unit tests check image validation, prompt construction, image payloads and response handling without making paid API calls:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Official image-input documentation: https://developers.openai.com/api/docs/guides/images-vision
