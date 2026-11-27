# NOVA

NOVA is an AI-powered desktop assistant for Windows. It provides a web-based chat interface, voice input and replies, OpenRouter model configuration with automatic fallback, Google search, application launching, and file operations subject to the selected access mode and the current Windows account permissions.

## Requirements

- Windows 10 or 11
- Python 3.10 or newer
- An OpenRouter API key

## Quick setup

1. Download or clone this repository.
2. Run `install.bat`.
3. Copy `.env.example` to `.env` (the installer creates it automatically if missing) and add your OpenRouter API key.
4. Run `start.bat`.
5. Use the local address shown in the terminal or scan the QR code on the connection page.

## Documentation

- [Complete user guide](USER_GUIDE.md) — installation, configuration, everyday examples, voice, phone connection, troubleshooting, and safe use.
- [Detailed project overview](README_EN.md)

## Access modes

Limited Access restricts file operations to the NOVA workspace. Full User Access follows the permissions of the currently signed-in Windows account; it does not automatically grant Administrator privileges.

## Author

Muhammad Taha Torabzadeh — [TahaDevX](https://github.com/TahaDevX) — MohammadTaha.dev@gmail.com
