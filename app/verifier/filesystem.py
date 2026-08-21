from typing import Any

from .base import BaseVerifier


class FilesystemVerifier(BaseVerifier):

    def verify(
        self,
        expected: dict[str, Any],
        actual: dict[str, Any],
    ) -> bool:

        for key, expected_value in expected.items():

            actual_value = actual.get(key)

            if actual_value != expected_value:
                return False

        return True