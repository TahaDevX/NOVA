import json
from openai import OpenAI, APIConnectionError, APITimeoutError, APIStatusError
from config import API_KEY, MODEL, FALLBACK_MODEL
from tools import TOOLS, FUNCTIONS, get_access_mode

SYSTEM = """You are NOVA, a multilingual Windows desktop assistant developed by Mohammad Taha Torabzadeh.

LANGUAGE BEHAVIOR (important):
- Detect the language of the user's latest message and reply in that same language.
- If the user switches languages (for example English, French, Persian, German, or Spanish), switch naturally and continue in the new language.
- Do not force English in the conversation. The application interface is English, but conversation language is chosen by the user.
- Keep tool arguments and paths exactly as needed; translate your explanations, not filenames or commands.

Understand natural-language requests and use tools to perform supported actions. Do not claim success unless a tool confirms it.
The user chooses either LIMITED or FULL USER access in NOVA settings. Current access mode: {mode}.
In FULL USER mode, use absolute Windows paths when the user gives them (for example D:\\Projects\\MyApp). You may manage files and folders only within permissions of the Windows account running NOVA. Do not claim administrator privileges. If Windows denies access, explain that Windows permissions are required.
In LIMITED mode, file operations are confined to the NOVA workspace. If a requested path is outside it, explain how to switch access mode in Settings.
For folder creation use create_folder. For file creation use create_file. For listing use list_directory. For copying/moving use the matching tools. For launching an installed program use open_application; common names include Chrome, Firefox, Edge, PyCharm, VS Code, Notepad and Calculator. For opening a folder use open_folder.
For a Google search where the user asks only to search, use google_search. If the user asks to open a numbered result (for example, 'search for X and open the second website'), use google_search_and_open with result_number set to that ordinal (second=2, third=3, etc.). These are organic results as parsed from Google; if Google blocks automated result retrieval, the tool will open the search page and explain that manual selection is needed.
Never overwrite an existing file unless the user explicitly asks. Never delete files, run arbitrary shell/PowerShell commands, change security settings, access credentials, or elevate privileges. Do not invent capabilities.
If a requested action is unsupported or blocked, clearly state why and offer a supported alternative.
"""

client = OpenAI(api_key=API_KEY or 'missing-api-key', base_url='https://openrouter.ai/api/v1', timeout=90.0, max_retries=1)

# Provider outages and transient gateway failures should not stop the whole assistant.
TRANSIENT_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}


def _is_transient_provider_error(exc):
    if isinstance(exc, (APIConnectionError, APITimeoutError, TimeoutError, ConnectionError)):
        return True
    if isinstance(exc, APIStatusError):
        return exc.status_code in TRANSIENT_STATUS_CODES
    status = getattr(exc, 'status_code', None)
    if status in TRANSIENT_STATUS_CODES:
        return True
    response = getattr(exc, 'response', None)
    response_status = getattr(response, 'status_code', None)
    return response_status in TRANSIENT_STATUS_CODES


def _create_completion(model, history):
    return client.chat.completions.create(
        model=model,
        messages=history,
        tools=TOOLS,
        tool_choice='auto',
        temperature=0.2,
    )


def ask(messages):
    history = [{'role': 'system', 'content': SYSTEM.format(mode=get_access_mode().upper())}]
    for item in messages[-24:]:
        if isinstance(item, dict) and item.get('role') in {'user', 'assistant'} and isinstance(item.get('content'), str):
            history.append({'role': item['role'], 'content': item['content'][:12000]})

    primary_model = MODEL
    fallback_model = FALLBACK_MODEL
    active_model = primary_model
    fallback_used = False
    last_error = None

    for _ in range(8):
        try:
            result = _create_completion(active_model, history)
        except Exception as exc:
            last_error = exc
            can_fallback = (
                not fallback_used
                and fallback_model
                and fallback_model != primary_model
                and _is_transient_provider_error(exc)
            )
            if can_fallback:
                print(f'NOVA MODEL FALLBACK: {primary_model} failed ({type(exc).__name__}); retrying with {fallback_model}.')
                active_model = fallback_model
                fallback_used = True
                continue
            raise

        msg = result.choices[0].message
        assistant = {'role': 'assistant', 'content': msg.content or ''}
        if msg.tool_calls:
            assistant['tool_calls'] = [
                {'id': c.id, 'type': 'function', 'function': {'name': c.function.name, 'arguments': c.function.arguments}}
                for c in msg.tool_calls
            ]
        history.append(assistant)

        if not msg.tool_calls:
            visible = [
                x for x in history[1:]
                if x.get('role') in {'user', 'assistant'}
                and isinstance(x.get('content'), str)
                and x.get('content').strip()
            ]
            return msg.content or 'Done.', visible, {
                'model_used': active_model,
                'fallback_used': fallback_used,
                'primary_model': primary_model,
            }

        for call in msg.tool_calls:
            try:
                fn = FUNCTIONS[call.function.name]
                args = json.loads(call.function.arguments or '{}')
                output = fn(**args)
            except Exception as exc:
                output = f'Tool execution error: {exc}'
            history.append({'role': 'tool', 'tool_call_id': call.id, 'name': call.function.name, 'content': str(output)[:12000]})

    visible = [
        x for x in history[1:]
        if x.get('role') in {'user', 'assistant'}
        and isinstance(x.get('content'), str)
        and x.get('content').strip()
    ]
    return 'This request required too many steps. Please split it into smaller requests.', visible, {
        'model_used': active_model,
        'fallback_used': fallback_used,
        'primary_model': primary_model,
    }
