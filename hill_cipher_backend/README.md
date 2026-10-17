# Hill Cipher Visualizer — Backend

FastAPI backend for an educational Hill Cipher dashboard. The API returns mathematical calculation steps for the frontend to visualize; it does not expose Python source code as the implementation walkthrough.

## Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API documentation.

## Endpoints

- `GET /health`
- `POST /api/cipher/encrypt`
- `POST /api/cipher/decrypt`
- `POST /api/cipher/validate-key`
- `GET /api/cipher/implementation`

Example request body:

```json
{
  "text": "HELP",
  "key_matrix": [[3, 3], [2, 5]]
}
```

Expected ciphertext: `HIAT`.

## Tests

```bash
python -m unittest discover -s tests -v
python -m unittest -v test_hill_cipher.py
```

The canonical calculation engine lives in `app/services/hill_cipher.py`. The root-level `hill_cipher.py` is a compatibility entry point for running the example and the original engine tests; it imports the canonical implementation.

This classical cipher is for learning and is not suitable for real-world data security.
