# Deploy To Streamlit Community Cloud

## App Entry Point

Use:

- `app/streamlit_app.py`

## Python Version

This repo includes:

- `runtime.txt` -> `python-3.11`

## Dependencies

This repo includes:

- `requirements.txt`

Packages required for the app:

- `streamlit`
- `pypdf`

## Deploy Steps

1. Push this repository to GitHub.
2. Open [https://share.streamlit.io](https://share.streamlit.io).
3. Click `New app`.
4. Select your GitHub repository.
5. Set:
   - Branch: your deployment branch
   - Main file path: `app/streamlit_app.py`
6. Click `Deploy`.

## Notes

- PDF uploads are supported through `pypdf`.
- The app also accepts pasted notes and other uploaded file types, but only files with extractable text will appear in the preview.
- If a file cannot be parsed, the app shows a warning instead of failing.
