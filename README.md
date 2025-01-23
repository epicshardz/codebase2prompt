# Codebase2Prompt

## Description
Codebase2Prompt is a minimal command-line tool that generates structured prompts from codebases. It does not provide the full function code, but purely the method addresses. It supports multiple output formats (Markdown, JSON, YAML) and automatically copies results to your clipboard. The tool is particularly useful for:
- Creating codebase overviews for AI prompts
- Generating documentation templates
- Sharing code context with collaborators

## Purpose

There are many times the LLM context window is maxed out when providing the full codebase. Because it is good practice to name functions with logical addresses, it goes to reason that a LLM will be able to intuit what a class, method, etc contains based on its naming and location in the folder structure. This is meant to provide high level understanding to the LLM in times where LLM drift becomes and issue. 

## Installation

### PyPI Installation
Install directly from PyPI:
```bash
pip install codebase2prompt
```

Verify installation:
```bash
c2p --version
```

### Development Installation
For local development:

1. Clone the repository:
```bash
git clone https://github.com/epicshardz/codebase2prompt
cd codebase2prompt
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Install the CLI tool:
```bash
poetry shell
pip install .
```

## Configuration
The tool can be configured using a `config.ini` file. Copy the example configuration:
```bash
c2p config.ini.example config.ini
```

### Configuration Options
- **Default Path**: Set the default directory to scan
- **File Extensions**: Specify which file types to include
- **Exclusion Patterns**: Define patterns to exclude files/directories
- **Output Format**: Choose between markdown, json, or yaml
- **Clipboard Settings**: Enable/disable automatic clipboard copying

## Usage

### Basic Usage
Scan the current directory:
```bash
c2p
```

Scan a specific directory:
```bash
c2p /path/to/codebase
```

### Excluding Files/Directories
Exclude specific patterns:
```bash
c2p --exclude node_modules --exclude .git
```

### Output Formats
Generate JSON output:
```bash
c2p --output-format json
```

Generate YAML output:
```bash
c2p --output-format yaml
```

### Clipboard Integration
Disable clipboard copying:
```bash
c2p --no-clipboard
```

Force clipboard copying:
```bash
c2p --clipboard
```

## Development

### Setting Up
1. Install development dependencies:
```bash
poetry install --with dev
```

2. Activate the virtual environment:
```bash
poetry shell
```

### Running Tests
Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=Codebase2Prompt
```

### Code Formatting
Format code with Black:
```bash
black .
```

Sort imports with isort:
```bash
isort .
```

### Building and Releasing
Build the package:
```bash
poetry build
```

Publish to PyPI:
```bash
poetry publish
```

## Contributing
We welcome contributions! Please follow these guidelines:
1. Open an issue to discuss proposed changes
2. Fork the repository and create a feature branch
3. Submit a pull request with:
   - Clear description of changes
   - Updated tests
   - Documentation updates if needed

For bug reports, please include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details
