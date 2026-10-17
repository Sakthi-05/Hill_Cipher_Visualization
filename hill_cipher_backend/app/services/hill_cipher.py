"""Hill Cipher calculation engine with structured mathematical walkthroughs.

Alphabet convention: A=0, B=1, ..., Z=25.
Vectors are columns and ciphertext/plaintext blocks are multiplied as K @ v mod 26.
This is an educational classical cipher, not suitable for real-world security.
"""

from __future__ import annotations

from math import gcd
from typing import Any, Sequence

MODULUS = 26


class HillCipherError(ValueError):
    """Raised when input text or a Hill Cipher key is invalid."""


def normalize_text(text: str) -> str:
    """Keep English letters only and convert them to uppercase."""
    if not isinstance(text, str):
        raise HillCipherError("Text must be a string.")
    normalized = "".join(ch for ch in text.upper() if "A" <= ch <= "Z")
    if not normalized:
        raise HillCipherError("Enter at least one English letter (A-Z).")
    return normalized


def text_to_numbers(text: str) -> list[int]:
    return [ord(ch) - ord("A") for ch in text]


def numbers_to_text(numbers: Sequence[int]) -> str:
    return "".join(chr((int(n) % MODULUS) + ord("A")) for n in numbers)


def mod_inverse(value: int, modulus: int = MODULUS) -> int:
    """Return the multiplicative inverse of value modulo modulus."""
    value %= modulus
    for candidate in range(1, modulus):
        if (value * candidate) % modulus == 1:
            return candidate
    raise HillCipherError(
        f"{value} has no multiplicative inverse modulo {modulus}; "
        "the key matrix is not invertible modulo 26."
    )


def determinant(matrix: Sequence[Sequence[int]]) -> int:
    """Calculate the determinant for a 2x2 or 3x3 matrix."""
    validate_matrix_shape(matrix)
    if len(matrix) == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def validate_matrix_shape(matrix: Sequence[Sequence[int]]) -> None:
    if not isinstance(matrix, (list, tuple)) or len(matrix) not in (2, 3):
        raise HillCipherError("Key matrix must be a 2x2 or 3x3 square matrix.")
    n = len(matrix)
    if any(not isinstance(row, (list, tuple)) or len(row) != n for row in matrix):
        raise HillCipherError("Key matrix must be square: either 2x2 or 3x3.")
    for row in matrix:
        for value in row:
            if isinstance(value, bool) or not isinstance(value, int):
                raise HillCipherError("Every key matrix entry must be an integer.")


def minor_matrix(matrix: Sequence[Sequence[int]], row_to_remove: int, col_to_remove: int) -> list[list[int]]:
    return [
        [value for j, value in enumerate(row) if j != col_to_remove]
        for i, row in enumerate(matrix)
        if i != row_to_remove
    ]


def adjugate(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return the adjugate matrix for a 2x2 or 3x3 matrix."""
    validate_matrix_shape(matrix)
    n = len(matrix)
    if n == 2:
        a, b = matrix[0]
        c, d = matrix[1]
        return [[d, -b], [-c, a]]

    cofactors: list[list[int]] = []
    for i in range(n):
        row_cofactors = []
        for j in range(n):
            minor_det = determinant(minor_matrix(matrix, i, j))
            row_cofactors.append(((-1) ** (i + j)) * minor_det)
        cofactors.append(row_cofactors)
    # Adjugate is the transpose of the cofactor matrix.
    return [[cofactors[j][i] for j in range(n)] for i in range(n)]


def inverse_matrix_mod26(matrix: Sequence[Sequence[int]]) -> tuple[list[list[int]], dict[str, Any]]:
    """Return inverse modulo 26 and the key calculations used to derive it."""
    validate_matrix_shape(matrix)
    det = determinant(matrix)
    det_mod = det % MODULUS
    if gcd(det_mod, MODULUS) != 1:
        raise HillCipherError(
            f"Invalid key: determinant {det} ≡ {det_mod} (mod 26), and "
            f"gcd({det_mod}, 26) = {gcd(det_mod, MODULUS)}. "
            "A valid Hill Cipher key requires gcd(det, 26) = 1."
        )
    det_inverse = mod_inverse(det_mod)
    adj = adjugate(matrix)
    inverse = [[(det_inverse * adj[i][j]) % MODULUS for j in range(len(matrix))] for i in range(len(matrix))]
    steps = {
        "determinant": det,
        "determinant_mod_26": det_mod,
        "gcd_determinant_26": gcd(det_mod, MODULUS),
        "determinant_inverse_mod_26": det_inverse,
        "adjugate_matrix": adj,
        "inverse_key_matrix": inverse,
    }
    return inverse, steps


def validate_key(matrix: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Describe whether a key is valid for encryption and decryption."""
    validate_matrix_shape(matrix)
    det = determinant(matrix)
    det_mod = det % MODULUS
    common_divisor = gcd(det_mod, MODULUS)
    result: dict[str, Any] = {
        "valid_shape": True,
        "dimension": len(matrix),
        "determinant": det,
        "determinant_mod_26": det_mod,
        "gcd_determinant_26": common_divisor,
        "invertible_mod_26": common_divisor == 1,
    }
    if common_divisor == 1:
        inverse, inverse_steps = inverse_matrix_mod26(matrix)
        result["inverse_key_matrix"] = inverse
        result["inverse_steps"] = inverse_steps
    else:
        result["reason"] = "The determinant is not coprime with 26, so no modular inverse exists."
    return result


def _multiply_matrix_vector(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> tuple[list[int], list[int], list[int]]:
    """Return raw products' sums, modulo-reduced values, and unreduced row totals."""
    row_totals = [sum(matrix[i][j] * vector[j] for j in range(len(vector))) for i in range(len(matrix))]
    reduced = [value % MODULUS for value in row_totals]
    return row_totals, reduced, row_totals


def _format_dot_products(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> list[dict[str, Any]]:
    expressions = []
    for i, row in enumerate(matrix):
        terms = [f"({row[j]} × {vector[j]})" for j in range(len(vector))]
        expressions.append({
            "row": i,
            "terms": terms,
            "expression": " + ".join(terms),
            "sum": sum(row[j] * vector[j] for j in range(len(vector))),
        })
    return expressions


def encrypt(plaintext: str, key: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Encrypt text and return each calculation step for frontend visualization."""
    validate_matrix_shape(key)
    original = normalize_text(plaintext)
    n = len(key)
    padding_count = (-len(original)) % n
    normalized = original + ("X" * padding_count)
    numeric_values = text_to_numbers(normalized)
    blocks = [numeric_values[i:i + n] for i in range(0, len(numeric_values), n)]
    output_numbers: list[int] = []
    block_steps: list[dict[str, Any]] = []

    for index, vector in enumerate(blocks):
        products, reduced, _ = _multiply_matrix_vector(key, vector)
        output_numbers.extend(reduced)
        block_steps.append({
            "block_index": index + 1,
            "input_letters": numbers_to_text(vector),
            "input_vector": vector,
            "key_matrix": [list(row) for row in key],
            "multiplication": _format_dot_products(key, vector),
            "raw_result_vector": products,
            "modulo": MODULUS,
            "modulo_calculation": [f"{value} mod 26 = {value % MODULUS}" for value in products],
            "output_vector": reduced,
            "output_letters": numbers_to_text(reduced),
        })

    return {
        "operation": "encrypt",
        "original_text": plaintext,
        "normalized_plaintext": original,
        "padding": {"character": "X", "count": padding_count, "padded_plaintext": normalized},
        "alphabet_mapping": "A=0, B=1, ..., Z=25",
        "key_matrix": [list(row) for row in key],
        "matrix_convention": "column vectors; C = K × P mod 26",
        "numeric_plaintext": numeric_values,
        "blocks": block_steps,
        "ciphertext": numbers_to_text(output_numbers),
        "steps": [
            {"number": 1, "title": "Normalize plaintext", "description": "Keep English letters A-Z and convert to uppercase."},
            {"number": 2, "title": "Pad into complete blocks", "description": f"The key is {n}×{n}; append {padding_count} X character(s) if needed."},
            {"number": 3, "title": "Convert letters to numbers", "description": "Map A to 0 through Z to 25."},
            {"number": 4, "title": "Multiply each block by the key matrix", "description": "Calculate C = K × P for each column vector."},
            {"number": 5, "title": "Reduce modulo 26", "description": "Take each result modulo 26 to return values to the range 0–25."},
            {"number": 6, "title": "Convert numbers to ciphertext", "description": "Map each reduced number back to an English letter."},
        ],
    }


def decrypt(ciphertext: str, key: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Decrypt text and return inverse-matrix derivation and each block calculation."""
    validate_matrix_shape(key)
    normalized = normalize_text(ciphertext)
    n = len(key)
    if len(normalized) % n != 0:
        raise HillCipherError(
            f"Ciphertext length ({len(normalized)}) must be divisible by the key dimension ({n}). "
            "Check that the ciphertext includes all padding characters."
        )

    inverse, inverse_steps = inverse_matrix_mod26(key)
    numeric_values = text_to_numbers(normalized)
    blocks = [numeric_values[i:i + n] for i in range(0, len(numeric_values), n)]
    output_numbers: list[int] = []
    block_steps: list[dict[str, Any]] = []

    for index, vector in enumerate(blocks):
        products, reduced, _ = _multiply_matrix_vector(inverse, vector)
        output_numbers.extend(reduced)
        block_steps.append({
            "block_index": index + 1,
            "input_letters": numbers_to_text(vector),
            "input_vector": vector,
            "inverse_key_matrix": inverse,
            "multiplication": _format_dot_products(inverse, vector),
            "raw_result_vector": products,
            "modulo": MODULUS,
            "modulo_calculation": [f"{value} mod 26 = {value % MODULUS}" for value in products],
            "output_vector": reduced,
            "output_letters": numbers_to_text(reduced),
        })

    return {
        "operation": "decrypt",
        "original_text": ciphertext,
        "normalized_ciphertext": normalized,
        "alphabet_mapping": "A=0, B=1, ..., Z=25",
        "key_matrix": [list(row) for row in key],
        "matrix_convention": "column vectors; P = K⁻¹ × C mod 26",
        "inverse_matrix_derivation": {
            "determinant_expression": "det(K)",
            "determinant": inverse_steps["determinant"],
            "determinant_mod_26": inverse_steps["determinant_mod_26"],
            "gcd_determinant_26": inverse_steps["gcd_determinant_26"],
            "determinant_inverse_mod_26": inverse_steps["determinant_inverse_mod_26"],
            "adjugate_matrix": inverse_steps["adjugate_matrix"],
            "inverse_key_matrix": inverse,
            "formula": "K⁻¹ = det(K)⁻¹ × adj(K) mod 26",
        },
        "numeric_ciphertext": numeric_values,
        "blocks": block_steps,
        "plaintext": numbers_to_text(output_numbers),
        "steps": [
            {"number": 1, "title": "Normalize ciphertext", "description": "Keep English letters A-Z and convert to uppercase."},
            {"number": 2, "title": "Calculate the determinant", "description": "Find det(K) and reduce it modulo 26."},
            {"number": 3, "title": "Check invertibility", "description": "The key is invertible only when gcd(det(K), 26) = 1."},
            {"number": 4, "title": "Find the modular inverse of the determinant", "description": "Find d⁻¹ such that d × d⁻¹ ≡ 1 (mod 26)."},
            {"number": 5, "title": "Calculate the adjugate and inverse key matrix", "description": "Compute K⁻¹ = det(K)⁻¹ × adj(K) mod 26."},
            {"number": 6, "title": "Multiply each ciphertext block", "description": "Calculate P = K⁻¹ × C for each column vector."},
            {"number": 7, "title": "Reduce modulo 26 and recover plaintext", "description": "Reduce each result modulo 26 and map numbers back to letters."},
        ],
    }


if __name__ == "__main__":
    sample_key = [[3, 3], [2, 5]]
    encrypted = encrypt("HELP", sample_key)
    decrypted = decrypt(encrypted["ciphertext"], sample_key)
    print("Plaintext : HELP")
    print("Ciphertext:", encrypted["ciphertext"])
    print("Recovered :", decrypted["plaintext"])
    print("First encryption block:", encrypted["blocks"][0])
