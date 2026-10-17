from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StrictInt

MatrixEntry = StrictInt
KeyMatrix = Annotated[list[list[MatrixEntry]], Field(min_length=2, max_length=3)]


class CipherRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: Annotated[str, Field(min_length=1, max_length=10000, description="Plaintext or ciphertext using English letters A-Z")]
    key_matrix: KeyMatrix


class KeyValidationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key_matrix: KeyMatrix
