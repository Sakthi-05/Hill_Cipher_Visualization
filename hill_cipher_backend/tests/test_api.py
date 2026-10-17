import unittest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
KEY = [[3, 3], [2, 5]]


class HillCipherApiTests(unittest.TestCase):
    def test_health(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_encrypt_returns_math_steps(self):
        response = client.post("/api/cipher/encrypt", json={"text": "HELP", "key_matrix": KEY})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ciphertext"], "HIAT")
        self.assertEqual(data["blocks"][0]["raw_result_vector"], [33, 34])
        self.assertEqual(data["blocks"][0]["output_vector"], [7, 8])
        self.assertIn("steps", data)

    def test_decrypt_returns_inverse_matrix_and_plaintext(self):
        response = client.post("/api/cipher/decrypt", json={"text": "HIAT", "key_matrix": KEY})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["plaintext"], "HELP")
        self.assertEqual(data["inverse_matrix_derivation"]["inverse_key_matrix"], [[15, 17], [20, 9]])

    def test_invalid_key_is_explained(self):
        response = client.post("/api/cipher/decrypt", json={"text": "TEST", "key_matrix": [[2, 4], [2, 6]]})
        self.assertEqual(response.status_code, 422)
        self.assertIn("gcd", response.json()["detail"])

    def test_validate_key(self):
        response = client.post("/api/cipher/validate-key", json={"key_matrix": KEY})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["invertible_mod_26"])

    def test_implementation_endpoint(self):
        response = client.get("/api/cipher/implementation")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["supported_key_dimensions"], [2, 3])


if __name__ == "__main__":
    unittest.main()
