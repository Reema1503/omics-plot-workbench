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
   - **Automatic AI:** enter your OpenAI API key and a vision model available to your account (default `gpt-4.1`, editable). Click Interpret. API usage is billed separately from a ChatGPT subscription.
4. Review and edit the interpretation. Download a Markdown report or a ZIP containing the report, figures, study details and prompt.

API keys are excluded from downloads and are not written to disk. You may instead supply `OPENAI_API_KEY` and `OPENAI_MODEL` environment variables. Figures and context are sent to OpenAI only when you click Interpret. Requests use `store: false`; this does not imply zero provider retention. Sessions are kept in memory; download work before closing. This app is intended for local use, without authentication; do not expose it publicly with a shared key.

The interpretation prompt asks for observations, provisional explanations, a combined interpretation, up to three next steps, a Results paragraph and individual captions. It prohibits invented details and significance/causation claims from figures alone. AI may still misread a figure; review every sample label, value and biological claim.

PDF and TIFF inputs are not supported; export those plots as PNG. This app cannot automatically retrieve plots from your previous chats. Upload them again in the dashboard.

## Verification

The included standard-library unit tests check image validation, prompt construction, image payloads and response handling without making paid API calls:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Official image-input documentation: https://developers.openai.com/api/docs/guides/images-vision
