# Hill Cipher Visualization Dashboard

An interactive web application that demonstrates Hill Cipher encryption and decryption using matrix multiplication and modular arithmetic.

**Live Demo:** [Try it here](https://hill-cipher-visualization-psi.vercel.app/)

## Tech Stack
- **Frontend:** React, Vite, JavaScript
- **Backend:** Python, FastAPI
- **Deployment:** Vercel, Render

## Features
- Encrypt and decrypt text using a key matrix.
- Explore matrix-based cryptographic transformations.
- Validate inputs and handle invalid keys.

## Run Locally

**Backend**
```bash
cd hill_cipher_backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend** (in a separate terminal)
```bash
cd hill_cipher_frontend
npm install
npm run dev
```

Backend API documentation: [View API Docs](https://hill-cipher-api.onrender.com/docs)

## Note
The Hill Cipher is intended for educational purposes and is not secure for modern encryption.

## Author
**Sakthi Mageswari V.** · [GitHub](https://github.com/Sakthi-05)
