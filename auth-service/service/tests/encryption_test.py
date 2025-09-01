import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from security.core.encryption import Encryption, SecurityOperations


def test_encrypt_decrypt_with_temp_key():
    """Test encryption/decryption with a temporary key file"""
    # Create a temporary key file for testing
    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".txt"
    ) as temp_key_file:
        # Create an encryption instance to generate a key
        encryption = Encryption()
        temp_key_file.write(encryption.key)
        temp_key_path = temp_key_file.name

    try:
        # Mock the path to use our temporary key file
        with patch.object(
            SecurityOperations,
            "__init__",
            lambda self: setattr(self, "path", temp_key_path),
        ):
            security_operations = SecurityOperations()

            # Test encryption and decryption
            original_message = "test_token"
            encrypted_token = security_operations.encrypt(original_message)

            assert encrypted_token is not None
            assert (
                encrypted_token != original_message
            )  # Should be different when encrypted

            decrypted_token = security_operations.decrypt(encrypted_token)
            assert decrypted_token == original_message
    finally:
        # Clean up temporary file
        os.unlink(temp_key_path)


def test_encrypt_decrypt_different_messages():
    """Test encryption/decryption with different messages"""
    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".txt"
    ) as temp_key_file:
        encryption = Encryption()
        temp_key_file.write(encryption.key)
        temp_key_path = temp_key_file.name

    try:
        with patch.object(
            SecurityOperations,
            "__init__",
            lambda self: setattr(self, "path", temp_key_path),
        ):
            security_operations = SecurityOperations()

            # Test with different messages
            messages = [
                "short",
                "a much longer message with spaces",
                "special!@#$%^&*()chars",
            ]

            for message in messages:
                encrypted = security_operations.encrypt(message)
                decrypted = security_operations.decrypt(encrypted)
                assert decrypted == message
    finally:
        os.unlink(temp_key_path)


@patch(
    "builtins.open",
    side_effect=FileNotFoundError("No such file or directory: 'key_store/key.txt'"),
)
def test_encrypt_with_missing_key_file(mock_open):
    """Test that encryption fails gracefully when key file is missing"""
    security_operations = SecurityOperations()

    with pytest.raises(FileNotFoundError):
        security_operations.encrypt("test")
