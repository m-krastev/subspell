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

    # GUI command
    gui_parser = subparsers.add_parser(
        "gui", help="Launch the graphical user interface"
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
    parser.add_argument(
        "--system-instruction",
        help="Inline system instruction text for the model",
    )
    parser.add_argument(
        "--system-instruction-file",
        help="Path to a file containing system instructions for the model",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Controls randomness in the output (0.0 to 1.0)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=40,
        help="Controls diversity via top-k sampling",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.95,
        help="Controls diversity via nucleus sampling",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.0-flash",
        help="The model to use (e.g. gemini-pro, gemini-pro-vision)",
    )

    # Parse arguments
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 1

    # Launch GUI if requested
    if parsed_args.command == "gui":
        try:
            from .gui import run_gui

            run_gui()
            return 0
        except Exception as e:
            print(f"Error launching GUI: {str(e)}", file=sys.stderr)
            return 1

    try:
        # Initialize spellchecker with selected provider
        spellchecker = SpellChecker(
            provider_name=parsed_args.provider,
            api_key=parsed_args.api_key,
            max_tokens_per_chunk=parsed_args.max_tokens,
            chunk_overlap=parsed_args.chunk_overlap,
            system_instruction=parsed_args.system_instruction,
            system_instruction_file=parsed_args.system_instruction_file,
            temperature=parsed_args.temperature,
            top_k=parsed_args.top_k,
            top_p=parsed_args.top_p,
            model=parsed_args.model,
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
