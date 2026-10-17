import unittest
from hill_cipher import encrypt, decrypt, validate_key, HillCipherError

class HillCipherTests(unittest.TestCase):
    def test_encrypt_example(self):
        result = encrypt("HELP", [[3, 3], [2, 5]])
        self.assertEqual(result["ciphertext"], "HIAT")
        self.assertEqual(result["blocks"][0]["output_vector"], [7, 8])

    def test_decrypt_round_trip(self):
        key = [[3, 3], [2, 5]]
        encrypted = encrypt("HELP", key)
        self.assertEqual(decrypt(encrypted["ciphertext"], key)["plaintext"], "HELP")

    def test_invalid_key_rejected_for_decryption(self):
        with self.assertRaises(HillCipherError):
            decrypt("TEST", [[2, 4], [2, 6]])

    def test_padding(self):
        result = encrypt("CAT", [[3, 3], [2, 5]])
        self.assertEqual(result["padding"]["count"], 1)
        self.assertEqual(result["padding"]["padded_plaintext"], "CATX")

    def test_3x3_round_trip(self):
        key = [[6, 24, 1], [13, 16, 10], [20, 17, 15]]
        encrypted = encrypt("ACT", key)
        self.assertEqual(decrypt(encrypted["ciphertext"], key)["plaintext"], "ACT")

    def test_validate_key(self):
        self.assertTrue(validate_key([[3, 3], [2, 5]])["invertible_mod_26"])
        self.assertFalse(validate_key([[2, 4], [2, 6]])["invertible_mod_26"])

if __name__ == "__main__":
    unittest.main()
