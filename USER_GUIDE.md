# NOVA User Guide

This guide explains how to install, configure, and use NOVA on Windows.

## 1. What NOVA does

NOVA is a local web interface connected to an AI model through OpenRouter. It can understand requests in several languages and perform the supported desktop actions exposed by the application, including:

- Chat with the assistant in your preferred language
- Launch supported installed applications
- Open websites and Google search pages
- Create, read, and organize files and folders
- Copy and move files and folders
- Choose between Limited Access and Full User Access
- Use speech input and optional spoken replies
- Connect a phone browser to the computer over the same local Wi-Fi network

NOVA does not have unrestricted control of Windows. It runs with the permissions of the Windows account that starts it.

## 2. Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer, with the Python Launcher (`py`)
- Internet access for package installation and AI requests
- An OpenRouter API key
- A modern browser such as Chrome or Edge

## 3. Install NOVA

1. Download the repository using **Code → Download ZIP**, then extract it to a folder you can access.
2. Install Python 3.10 or newer if it is not already installed. During installation, enable the option to add Python to PATH.
3. Open the extracted NOVA folder.
4. Double-click `install.bat`.
5. Wait for the installer to create a virtual environment and install the required packages.
6. When installation finishes, open the `.env` file in a text editor.

If Windows says Python cannot be found, install Python and make sure the Python Launcher is available, then run `install.bat` again.

## 4. Configure OpenRouter

1. Open the `.env` file in the NOVA folder.
2. Set `OPENROUTER_API_KEY` to your own OpenRouter API key.
3. Optionally change `OPENROUTER_MODEL` and `OPENROUTER_FALLBACK_MODEL`.
4. Save the file.

Example configuration:

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=google/gemini-2.5-flash
OPENROUTER_FALLBACK_MODEL=openai/gpt-4o-mini
APP_HOST=0.0.0.0
APP_PORT=8000
PYCHARM_PATH=
```

Keep your real `.env` file private. Do not upload it or share your API key. The repository includes `.env.example` as a safe template.

## 5. Start NOVA

1. Double-click `start.bat`.
2. A terminal window starts the local server.
3. Your browser should open the NOVA connection page.
4. If it does not open automatically, visit `http://127.0.0.1:8000/connect` (unless you changed `APP_PORT`).

Keep the terminal window open while using NOVA. Closing it stops the server.

## 6. Chat with NOVA

Type a request in the message box and press Enter or select the Send button. Use Shift + Enter to add a new line.

Examples:

- "Open Google Chrome."
- "Open PyCharm."
- "Create a folder named PythonPractice in my workspace."
- "Create a file named hello.py in my workspace with a Hello World program."
- "List the files in my workspace."
- "Search Google for the official FastAPI documentation."
- "Open the second Google result for Python virtual environments."

Be specific about file names and locations. NOVA should report when an action is unsupported or blocked rather than claiming it succeeded.

## 7. Choose computer access

Open the gear icon in the NOVA header to open Settings.

### Limited Access

File and folder operations are restricted to the NOVA `workspace` folder. This is the safer option for trying the application.

### Full User Access

NOVA can work with paths permitted to the Windows account currently running it. It does not grant Administrator privileges, bypass Windows security, or guarantee access to protected folders. If Windows denies access, run only the appropriate actions with an account that already has permission.

NOVA's supported tools are intentionally limited. It does not provide arbitrary command-line or PowerShell execution.

## 8. Use voice

### Speech input

1. Select the input language from the **Voice language** menu.
2. Select the microphone button.
3. Allow microphone access if your browser asks.
4. Speak your request. NOVA submits the recognized text when speech recognition ends.

Speech recognition support depends on the browser and its language services. Chrome generally provides the best compatibility.

### Spoken replies

Select the speaker icon in the top bar to turn spoken replies on or off. The browser's available speech voices and language support determine how replies sound.

## 9. Connect a phone

1. Start NOVA on the computer.
2. On the connection page, find the QR code or local network address.
3. Connect the phone and computer to the same Wi-Fi network.
4. Scan the QR code with the phone camera, or enter the displayed address in the phone browser.

The local HTTP connection is intended for use on a trusted local network. Some mobile browsers restrict microphone access on ordinary HTTP LAN addresses because they are not considered secure contexts. If microphone access is unavailable on the phone, use text input or configure a trusted HTTPS connection separately.

Do not expose NOVA's server directly to the public internet.

## 10. Troubleshooting

**NOVA says the API key is not configured**
- Confirm that the file is named `.env` (not `.env.txt`).
- Check that `OPENROUTER_API_KEY` contains a valid key.
- Restart NOVA after editing the file.

**The AI service cannot be reached**
- Check your internet connection.
- Check the OpenRouter account, API key, model availability, and any network restrictions.
- Some networks may require a VPN or different connection.
- NOVA can retry a transient provider failure with the configured fallback model.

**A program cannot be opened**
- Confirm that the application is installed.
- Try its common name, such as Chrome, Firefox, Edge, PyCharm, VS Code, Notepad, or Calculator.
- Some applications may not be discoverable automatically.

**A file operation is blocked**
- Check whether Limited Access is selected.
- In Limited Access, use a path inside the NOVA workspace.
- Full User Access still follows Windows account permissions.

**The phone cannot connect**
- Confirm both devices use the same Wi-Fi network.
- Allow Python through Windows Firewall on private networks if Windows asks.
- Use the exact address shown on the connection page.
- Check that the configured port is not blocked or already in use.

**The microphone is unavailable**
- Allow microphone access in browser site settings.
- Check that the correct microphone is selected in Windows.
- Try Chrome and verify that the selected speech language is supported.
- On a phone using a local HTTP address, browser secure-context restrictions may prevent microphone access.

## 11. Stop NOVA

Close the terminal window running the server, or press Ctrl + C in that window.

## 12. Privacy and safe use

- Keep your OpenRouter API key in the local `.env` file and never commit that file.
- Use Limited Access unless broader file access is genuinely needed.
- Do not expose the local server to untrusted networks or the public internet.
- Review file paths before asking NOVA to create, copy, or move data.
- NOVA does not elevate privileges or bypass Windows access controls.
