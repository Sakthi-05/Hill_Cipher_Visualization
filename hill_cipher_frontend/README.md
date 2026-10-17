# Hill Cipher Lab — Frontend

React + Vite frontend for the Hill Cipher mathematical visualizer. The UI calls a FastAPI backend and renders the calculation response as an interactive step walkthrough.

## Requirements
- Node.js 18+
- The Hill Cipher FastAPI backend running on `http://127.0.0.1:8000`

## Run locally
```bash
npm install
npm run dev
```
Open the Vite URL printed in the terminal (usually `http://localhost:5173`).

## Configure backend URL
By default, the frontend calls `http://127.0.0.1:8000`. To override it, create `.env` in this folder:
```env
VITE_API_URL=http://127.0.0.1:8000
```
Restart Vite after changing `.env`.

## Features
- Encrypt and decrypt controls
- Editable 2x2 and 3x3 key matrices
- Key validation endpoint integration
- Result overview and copy button
- Previous/next walkthrough controls
- Calculation details rendered from the API response
- FastAPI `/docs` shortcut

## Notes
The Hill Cipher is an educational classical cipher and must not be used to protect real sensitive data.
