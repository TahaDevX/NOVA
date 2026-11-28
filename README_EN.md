# NOVA - Intelligent Desktop Assistant

Developed by **Mohammad Taha Torabzadeh** ([TahaDevX](https://github.com/TahaDevX)).  
Contact: [MohammadTaha.dev@gmail.com](mailto:MohammadTaha.dev@gmail.com)

## Features
- Multilingual AI conversation: NOVA is instructed to reply in the language of the user's latest message. The application interface remains English.
- Automatic AI model fallback: if the primary model returns a temporary provider/gateway error (including 408, 429, 500, 502, 503, or 504) or a connection timeout, NOVA retries the request with a separately configured backup model. The interface reports when the backup model was used.
- Optional browser-based voice input and spoken replies.
- Launch installed desktop applications by name, including Chrome, Edge, Firefox, PyCharm, VS Code, Notepad, and Calculator when detected.
- Create, read, list, copy, move, and open files/folders using the selected access mode.
- Google search in the default browser.
- Search Google and open a numbered organic result (for example, the second result).
- Responsive web interface for desktop and mobile browsers.
- Automatic phone connection page with QR codes and copyable LAN addresses at startup.

## Requirements
- Windows 10/11 recommended
- Python 3.10 or newer
- OpenRouter API key
- Internet connection; VPN may be required depending on network/provider access

## Installation
1. Extract the ZIP to a normal folder (avoid `Program Files` for the first run).
2. Install Python 3.10+ and enable **Add Python to PATH** during installation.
3. Run `install.bat`.
4. Open `.env` and set `OPENROUTER_API_KEY` and, if desired, `OPENROUTER_MODEL`.
5. Optionally set `OPENROUTER_FALLBACK_MODEL` to another tool-capable OpenRouter model. The default backup is `openai/gpt-4o-mini`; both models use your OpenRouter account and balance.
6. Run `start.bat`. NOVA automatically opens a **Connect your phone to NOVA** page on the computer.
7. Scan a QR code with your phone camera, or type the displayed address into your phone browser.
8. Keep NOVA running and connect the phone and computer to the same Wi-Fi network. If the QR page does not open automatically, visit `http://127.0.0.1:8000/connect` on the computer. Microphone support on a LAN HTTP address varies by browser and may require HTTPS.

## Access modes
- **Limited Access:** file operations are confined to the `workspace` folder.
- **Full User Access:** file operations can use paths accessible to the Windows account running NOVA. This does not elevate the process or grant Administrator privileges.

## Google result opening
When asked to search and open a numbered result, NOVA attempts to retrieve Google's server-rendered result page, parse organic results, and open the requested numbered link in the default browser. Google may change its page structure, apply bot protection, show a consent page, or block automated retrieval. If this happens, NOVA opens the Google results page and asks the user to select the result manually. The numbered result is the organic result order, not an advertisement or sponsored listing.

## Voice input
Select the spoken language from the **Voice language** menu before using the microphone. Text chat is multilingual and does not require changing this setting. Voice recognition and speech synthesis depend on browser support, internet access, and installed browser/system voices.

## Safety and limitations
- NOVA does not run arbitrary CMD/PowerShell commands, delete files, access saved credentials, change Windows security settings, or elevate privileges.
- File operations can fail when Windows denies access or a file is locked.
- Google result extraction is best-effort and may fail if Google changes its page or blocks automated requests.
- The OpenRouter API and voice features require a working internet connection. API access was not verified as part of packaging.

## Automatic model fallback
- `OPENROUTER_MODEL` is the primary model.
- `OPENROUTER_FALLBACK_MODEL` is the backup model (default: `openai/gpt-4o-mini`).
- On temporary provider errors or connection timeouts, NOVA switches to the backup for the remainder of that chat request, including tool-calling steps. It does not silently switch for ordinary configuration/authentication errors such as 401/403 or most 400 errors.
- The backup model is also billed through your OpenRouter account. Make sure your account can access it and that it supports tool calling. Set the value to blank to disable automatic fallback.

## User documentation
See [USER_GUIDE.md](USER_GUIDE.md) for step-by-step installation, examples, phone connection, troubleshooting, and safe-use guidance.

## Author
**Mohammad Taha Torabzadeh**  
GitHub: [@TahaDevX](https://github.com/TahaDevX)  
Email: [MohammadTaha.dev@gmail.com](mailto:MohammadTaha.dev@gmail.com)
