"""
Module used to test the commit message hook script.
"""
import sys
import tempfile

import pytest

from scripts.check_commit_message import main as check_commit_message_function


# Functions.
def write_commit_message_to_temp_file(commit_message: str) -> str:
    """
    Helper function to write a commit message to a temporary file and return the file path.

    Args:
        commit_message (str): The commit message to write to the temporary file.

    Returns:
        str: The file path of the temporary file containing the commit message.
    """
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as temp_file:
        temp_file.write(commit_message)
        return temp_file.name

def read_commit_message_from_temp_file(file_path: str) -> str:
    """
    Helper function to read a commit message from a temporary file.

    Args:
        file_path (str): The file path of the temporary file containing the commit message.

    Returns:
        str: The commit message read from the temporary file.
    """
    with open(file=file_path, mode="r", encoding="utf-8") as temp_file:
        return temp_file.read().strip()

def run_check_commit_message_function_with_temp_file(commit_message: str) -> str:
    """
    Helper function to run the check_commit_message_function with a commit message written to a temporary file.

    Args:
        commit_message (str): The commit message to write to the temporary file and validate.

    Returns:
        str: The formatted commit message returned by the check_commit_message_function.
    """
    temp_file_path = write_commit_message_to_temp_file(commit_message=commit_message)
    sys.argv = ["check_commit_message.py", temp_file_path]
    check_commit_message_function()
    return read_commit_message_from_temp_file(file_path=temp_file_path)

# Mocks.
@pytest.fixture
def valid_commit_message_list() -> list[tuple[str, str]]:
    """
    Fixture that returns a list of valid commit messages for testing.
    """
    return [
        ("feat: Add new feature to the project.", "✨ feat: Add new feature to the project."),
        ("fix: Fix a bug in the codebase.", "🐛 fix: Fix a bug in the codebase."),
        ("docs: Update documentation for the project.", "📝 docs: Update documentation for the project."),
        ("style: Improve code formatting and style.", "💄 style: Improve code formatting and style."),
        ("refactor: Refactor code for better readability.", "♻️ refactor: Refactor code for better readability."),
        ("test: Add new tests for the project.", "✅ test: Add new tests for the project."),
        ("chore: Update dependencies and perform maintenance.", "🔧 chore: Update dependencies and perform maintenance."),
        ("revert: Revert a previous commit.", "⏪ revert: Revert a previous commit.")
    ]

@pytest.fixture
def valid_but_unformatted_commit_message_list() -> list[tuple[str, str]]:
    """
    Fixture that returns a list of valid but unformatted commit messages for testing.
    """
    return [
        ("feat: add new function and improve performance", "✨ feat: Add new function and improve performance."),
        ("docs: update README. add usage examples", "📝 docs: Update README. Add usage examples."),
        ("revert: revert previous commit that introduced a bug...", "⏪ revert: Revert previous commit that introduced a bug."),
        ("fix: Fix issue related to user authentication..  validate user input and handle edge cases", "🐛 fix: Fix issue related to user authentication. Validate user input and handle edge cases.")
    ]

@pytest.fixture
def invalid_commit_message_list() -> list[str]:
    """
    Fixture that returns a list of invalid commit messages for testing.
    """
    return [
        "feat Add new feature to the project.",
        "test: Is this working?",
        "Update documentation for the project."
    ]

# Tests.
def test_valid_commit_message(valid_commit_message_list: list[tuple[str, str]]) -> None:
    """
    Test that valid commit messages are accepted by the check_commit_message_function.
    """
    # Validate git commit messages.
    for message, expected_message in valid_commit_message_list:
        formatted_message = run_check_commit_message_function_with_temp_file(commit_message=message)
        assert formatted_message == expected_message

def test_valid_but_unformatted_commit_message(valid_but_unformatted_commit_message_list: list[tuple[str, str]]) -> None:
    """
    Test that valid but unformatted commit messages are accepted and formatted by the check_commit_message_function.
    """
    # Validate git commit messages.
    for message, expected_message in valid_but_unformatted_commit_message_list:
        formatted_message = run_check_commit_message_function_with_temp_file(commit_message=message)
        assert formatted_message == expected_message

def test_invalid_commit_message(invalid_commit_message_list: list[str]) -> None:
    """
    Test that invalid commit messages are rejected by the check_commit_message_function.
    """
    # Validate git commit messages.
    for message in invalid_commit_message_list:
        with pytest.raises(SystemExit):
            run_check_commit_message_function_with_temp_file(commit_message=message)
