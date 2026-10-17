from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.cipher import router as cipher_router

app = FastAPI(
    title="Hill Cipher Visualizer API",
    description=(
        "An educational API for Hill Cipher encryption and decryption. "
        "Responses include structured mathematical steps for a frontend visualizer."
    ),
    version="1.0.0",
)

# React + Vite development server. Tighten this list for your actual deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://hill-cipher-visualization-psi.vercel.app"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(cipher_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Hill Cipher Visualizer API is running.",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
