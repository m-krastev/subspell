# SpellCheck

A command-line tool for spell checking and grammar correction in Bulgarian text, with special support for subtitle files (.srt and .ass).

## Features

- Spelling, punctuation, and grammar correction for Bulgarian text
- Support for subtitle files (.srt and .ass/ssa formats)
- Batch processing to optimize resource usage
- Preserves subtitle formatting and timings
- Command-line interface for easy integration

## Installation

### Prerequisites

- Python 3.10 or higher
- A Gemini API key ([Get one here](https://ai.google.dev/))

### Install from Source

```bash
# Clone the repository
git clone https://github.com/your-username/spellcheck.git
cd spellcheck

# Install the package
pip install -e .
```

### Configuration

Set your Gemini API key as an environment variable:

```bash
export GEMINI_API_KEY="your-api-key"
```

Or provide it with the `--api-key` option when running the tool.

## Usage

### Correcting Text

```bash
spellcheck text "Какво ще правябрат ми жена не ме е остъвила."
```

### Correcting Subtitle Files

```bash
# Correct an SRT file
spellcheck file path/to/subtitles.srt

# Correct an ASS file with custom output path
spellcheck file path/to/subtitles.ass -o path/to/corrected.ass

# Use token-based batching (default)
spellcheck file path/to/subtitles.srt --batch-size 0

# Use fixed batch size
spellcheck file path/to/subtitles.srt --batch-size 10
```

### Advanced Options

```bash
# Set maximum tokens per chunk
spellcheck file path/to/subtitles.srt --max-tokens 4000

# Set chunk overlap size
spellcheck file path/to/subtitles.srt --chunk-overlap 150

# Use a different provider (if implemented)
spellcheck file path/to/subtitles.srt --provider alternative-provider
```

## Development

### Project Structure

- `src/spellcheck/` - Main package
  - `spellchecker.py` - Core correction functionality
  - `subtitle.py` - Subtitle parsing and writing
  - `cli.py` - Command-line interface
  - `utils.py` - Utility functions
  - `providers/` - Model providers
    - `gemini.py` - Gemini API integration

### Adding a New Provider

To add a new provider:

1. Create a new file in the `providers` directory
2. Implement the `ModelProvider` interface
3. Update the `_get_provider` method in `SpellChecker` class

## License

This project is licensed under the MIT License - see the LICENSE file for details.
