# SubSpell

A subtitle spelling, punctuation and grammar correction tool with a modern GUI.

## Features

- Modern, user-friendly GUI
- Support for SRT and ASS/SSA subtitle formats
- Powered by Google's Gemini AI
- Configurable LLM parameters
- Dark/Light theme support
- Real-time diff view of changes

## Installation

### Pre-built Executables

Pre-built executables are available for Windows, macOS, and Linux in the [GitHub Releases](https://github.com/mkrastev/subspell/releases) page.

### Building from Source

#### Prerequisites

- Python 3.10 or higher
- Windows, macOS, or Linux

#### Build Steps

1. Clone the repository:
```bash
git clone https://github.com/mkrastev/subspell.git
cd subspell
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Run the build script:
```bash
python build_gui.py
```

The executable will be created in the `dist` directory.

### Development Builds

Development builds are automatically created for each push to the main branch and pull request. You can find these builds in the [GitHub Actions](https://github.com/mkrastev/subspell/actions) page.

## Usage

1. Launch the application
2. Configure your Gemini API key in the Tools menu
3. Open a subtitle file (SRT or ASS/SSA)
4. Click "Check Spelling" to start the correction process
5. Review and apply changes as needed
6. Save the corrected subtitle file

## Configuration

The application supports various configuration options:

- LLM Prompt: Customize the instructions given to the AI
- Temperature: Control randomness in the output (0.0-1.0)
- Top K: Control diversity via top-k sampling (1-100)
- Top P: Control diversity via nucleus sampling (0.0-1.0)
- Model: Choose between different Gemini models

## Development

### Project Structure

- `src/subspell/` - Main package
  - `spellchecker.py` - Core correction functionality
  - `subtitle.py` - Subtitle parsing and writing
  - `cli.py` - Command-line interface
  - `gui.py` - Graphical user interface
  - `config.py` - Configuration management
  - `providers/` - Model providers
    - `base.py` - Base provider interface
    - `gemini.py` - Gemini API integration

### Adding a New Provider

To add a new provider:

1. Create a new file in the `providers` directory
2. Implement the `ModelProvider` interface
3. Update the `_get_provider` method in `SpellChecker` class

### Continuous Integration

The project uses GitHub Actions for continuous integration:

- Builds executables for Windows, macOS, and Linux
- Creates GitHub releases when tags are pushed
- Runs on every push to main and pull request

## License

MIT License - see LICENSE file for details
