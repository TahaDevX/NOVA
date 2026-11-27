# NOVA

NOVA is an AI-powered desktop assistant for Windows. It provides a web-based chat interface, voice input and replies, OpenRouter model configuration with automatic fallback, Google search, application launching, and file operations subject to the selected access mode and the current Windows account permissions.

## Requirements

- Windows 10 or 11
- Python 3.10 or newer
- An OpenRouter API key

## Setup

1. Download or clone this repository.
2. Run `install.bat`.
3. Copy `.env.example` to `.env` and add your OpenRouter API key.
4. Run `start.bat` and open the local address shown in the terminal.

## Configuration

Set `OPENROUTER_API_KEY` and, if desired, `OPENROUTER_MODEL` and `OPENROUTER_FALLBACK_MODEL` in `.env`.

## Access modes

Limited Access restricts file operations to the NOVA workspace. Full User Access follows the permissions of the currently signed-in Windows account; it does not automatically grant Administrator privileges.

## Author

Muhammad Taha Torabzadeh — [TahaDevX](https://github.com/TahaDevX) — MohammadTaha.dev@gmail.com
