"""Compatibility entry point for the Hill Cipher calculation engine.

The canonical implementation lives in app.services.hill_cipher and is used by
both the API and this script, so the algorithm has a single source of truth.
"""
from app.services.hill_cipher import (  # noqa: F401
    HillCipherError,
    adjugate,
    decrypt,
    determinant,
    encrypt,
    inverse_matrix_mod26,
    mod_inverse,
    normalize_text,
    numbers_to_text,
    text_to_numbers,
    validate_key,
)


if __name__ == "__main__":
    sample_key = [[3, 3], [2, 5]]
    encrypted = encrypt("HELP", sample_key)
    decrypted = decrypt(encrypted["ciphertext"], sample_key)
    print("Plaintext : HELP")
    print("Ciphertext:", encrypted["ciphertext"])
    print("Recovered :", decrypted["plaintext"])
    print("First encryption block:", encrypted["blocks"][0])
