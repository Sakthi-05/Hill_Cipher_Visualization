from fastapi import APIRouter, HTTPException

from app.schemas import CipherRequest, KeyValidationRequest
from app.services.hill_cipher import HillCipherError, decrypt, encrypt, validate_key

router = APIRouter(prefix="/api/cipher", tags=["Hill Cipher"])


def run_calculation(operation, text: str, key_matrix: list[list[int]]):
    try:
        return operation(text, key_matrix)
    except HillCipherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/encrypt", summary="Encrypt plaintext and return mathematical steps")
def encrypt_text(payload: CipherRequest):
    """Encrypt text and return the result plus all per-block calculation details."""
    return run_calculation(encrypt, payload.text, payload.key_matrix)


@router.post("/decrypt", summary="Decrypt ciphertext and return mathematical steps")
def decrypt_text(payload: CipherRequest):
    """Decrypt text and return inverse-key derivation plus all per-block details."""
    return run_calculation(decrypt, payload.text, payload.key_matrix)


@router.post("/validate-key", summary="Validate a key matrix")
def validate_key_matrix(payload: KeyValidationRequest):
    """Check matrix dimensions and whether its determinant is invertible modulo 26."""
    try:
        return validate_key(payload.key_matrix)
    except HillCipherError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/implementation", summary="Get the mathematical method used by the visualizer")
def get_implementation():
    """Return frontend-friendly descriptions of the algorithm, not Python source code."""
    return {
        "alphabet_mapping": "A=0, B=1, ..., Z=25",
        "supported_key_dimensions": [2, 3],
        "vector_convention": "Column vectors",
        "encryption_formula": "C = K × P mod 26",
        "decryption_formula": "P = K⁻¹ × C mod 26",
        "key_validity_condition": "gcd(det(K), 26) = 1",
        "decryption_inverse_formula": "K⁻¹ = det(K)⁻¹ × adj(K) mod 26",
        "encryption_steps": [
            "Normalize the plaintext to uppercase English letters A-Z.",
            "Pad with X characters until the text length is divisible by the key dimension.",
            "Convert each letter to a number from 0 to 25.",
            "Group the numbers into column vectors.",
            "Multiply each vector by the key matrix.",
            "Reduce each value modulo 26 and convert values back to letters.",
        ],
        "decryption_steps": [
            "Normalize the ciphertext to uppercase English letters A-Z.",
            "Calculate det(K) and check gcd(det(K), 26) = 1.",
            "Find the modular multiplicative inverse of det(K).",
            "Calculate the adjugate and inverse key matrix modulo 26.",
            "Multiply each ciphertext vector by the inverse key matrix.",
            "Reduce modulo 26 and convert values back to plaintext letters.",
        ],
        "security_note": "The Hill Cipher is educational and should not be used to protect real sensitive data.",
    }
