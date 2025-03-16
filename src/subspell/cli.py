import argparse
import sys
import os
from typing import List

from .spellchecker import SpellChecker


def main(args: List[str] = None) -> int:
    """
    Main entry point for the command-line interface.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Spellcheck and correct text or subtitle files."
    )

    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Text correction command
    text_parser = subparsers.add_parser("text", help="Correct text")
    text_parser.add_argument("text", help="Text to correct")

    # File correction command
    file_parser = subparsers.add_parser("file", help="Correct subtitle file")
    file_parser.add_argument("filepath", help="Path to subtitle file (SRT or ASS)")
    file_parser.add_argument("-o", "--output", help="Path to save corrected file")
    file_parser.add_argument(
        "--batch-size",
        type=int,
        default=0,
        help="Number of subtitle entries to process in a batch (0 for token-based batching)",
    )

    # Common options
    parser.add_argument("--provider", default="gemini", help="Model provider to use")
    parser.add_argument("--api-key", help="API key for the provider")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=5000,
        help="Maximum tokens per chunk for batch processing",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Number of tokens to overlap between chunks",
    )

    # Parse arguments
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 1

    try:
        # Initialize spellchecker with selected provider
        spellchecker = SpellChecker(
            provider_name=parsed_args.provider,
            api_key=parsed_args.api_key,
            max_tokens_per_chunk=parsed_args.max_tokens,
            chunk_overlap=parsed_args.chunk_overlap,
        )

        # Handle commands
        if parsed_args.command == "text":
            corrected_text = spellchecker.correct_text(parsed_args.text)
            print(corrected_text)
            return 0

        elif parsed_args.command == "file":
            output_file = spellchecker.correct_subtitle_file(
                parsed_args.filepath,
                output_filepath=parsed_args.output,
                batch_size=parsed_args.batch_size,
            )
            print(f"Corrected file saved to: {output_file}")
            return 0

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())


# Add a run function that can be called directly when importing this module
def run():
    """Run the CLI application."""
    sys.exit(main())
