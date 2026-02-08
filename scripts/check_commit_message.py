"""
This script is a custom hook for pre-commit that checks if the commit message follows the expected
format. Then, it formats the commit message to match the project conventions.
"""

import re
import sys
from enum import Enum
from pathlib import Path


# Enums.
class CommitType(Enum):
    """
    Enum representing the valid commit types for the project.
    """

    FEAT = ("feat", "✨")
    FIX = ("fix", "🐛")
    DOCS = ("docs", "📝")
    STYLE = ("style", "💄")
    REFACTOR = ("refactor", "♻️")
    TEST = ("test", "✅")
    OPS = ("ops", "🚀")
    CHORE = ("chore", "🔧")
    REVERT = ("revert", "⏪")


# Functions.
def main(log: bool = True) -> None:
    """
    Entry point for the script.

    Args:
        log (bool): Whether to log the results to the console. Defaults to True.
    """

    # Log utility.
    def logger(message: str):
        print(message) if log else None

    # Get the commit message from arguments.
    try:
        commit_msg_filepath = sys.argv[1]
        commit_message = Path(commit_msg_filepath).read_text(encoding="utf-8").strip()
    except Exception as e:
        logger("Error: Unable to read the commit message file. " + str(e))
        sys.exit(1)

    # Extract the commit message from the match object.
    commit_type_list = [ct.value[0] for ct in CommitType]
    commit_message_pattern_re = re.compile(pattern=r"^(" + "|".join(commit_type_list) + r"):\s*(.+)$", flags=re.DOTALL)
    valid_commit_message_match = commit_message_pattern_re.match(string=commit_message)
    if not valid_commit_message_match:
        logger(
            "Error: Invalid commit message format. Please use the following format: "
            "<type>: <description> where <type> is one of " + ", ".join(commit_type_list) + " "
            "and <description> is a brief description of the changes (10-128 characters)."
        )
        sys.exit(1)

    # Check commit message description length.
    commit_type = valid_commit_message_match.group(1)
    commit_description = valid_commit_message_match.group(2).strip()

    non_character_pattern_re = re.compile(pattern=r"[^\w]+")
    commit_description_without_non_characters = non_character_pattern_re.sub(repl="", string=commit_description)
    if len(commit_description_without_non_characters) < 10 or len(commit_description_without_non_characters) > 128:
        logger(
            "Error: Invalid commit message description length. "
            "The description should be between 10 and 128 characters, "
            "excluding non-character symbols."
        )
        sys.exit(1)
    del commit_description_without_non_characters

    # Trim the commit description.
    trim_whitespace_re = re.compile(pattern=r"\s+")
    commit_description = trim_whitespace_re.sub(repl=" ", string=commit_description)

    # Block invalid characters in the commit description.
    invalid_characters_re = re.compile(pattern=r"[^a-zA-Z0-9 _.,\-\/()\[\]\"':;]")
    if invalid_characters_re.search(string=commit_description):
        logger(
            "Error: Invalid characters found in the commit message description. "
            "Only alphanumeric characters and common punctuation are allowed."
        )
        sys.exit(1)

    # Remove duplicate non-character symbols from the commit description.
    remove_duplicate_non_characters_re = re.compile(pattern=r"([^\w])\1+")
    commit_description = remove_duplicate_non_characters_re.sub(repl=r"\1", string=commit_description)

    # Capitalize the first letter of the commit description and
    # after any final dot.
    commit_description = commit_description[0].upper() + commit_description[1:]

    def capitalize_after_final_dot(match: re.Match) -> str:
        return match.group(0).capitalize()

    capitalize_after_final_dot_re = re.compile(pattern=r"(?<=\.\s)(\w)")
    commit_description = capitalize_after_final_dot_re.sub(repl=capitalize_after_final_dot, string=commit_description)

    # Add only one final dot at the end of the commit description if it doesn't already have one.
    final_dot_re = re.compile(pattern=r"\.*$")
    commit_description = final_dot_re.sub(repl="", string=commit_description)
    commit_description += "."

    # Get the corresponding emoji for the commit type.
    commit_type_emoji = CommitType[commit_type.upper()]
    commit_type_emoji_str = commit_type_emoji.value[1]

    # Format the commit message to match the project conventions.
    formatted_commit_message = f"{commit_type_emoji_str} {commit_type}: {commit_description}"

    # Write the formatted commit message back to the file.
    Path(commit_msg_filepath).write_text(formatted_commit_message, encoding="utf-8")


if __name__ == "__main__":
    main()
