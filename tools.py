"""NOVA desktop actions with user-selectable filesystem scope."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import webbrowser
import json
from urllib.parse import quote, urlparse, parse_qs
from html.parser import HTMLParser
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
WORKSPACE = (ROOT / 'workspace').resolve()
SETTINGS_FILE = ROOT / 'settings.json'
WORKSPACE.mkdir(exist_ok=True)

def get_access_mode():
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))
        return 'full' if data.get('access_mode') == 'full' else 'limited'
    except Exception:
        return 'limited'

def set_access_mode(mode: str):
    if mode not in {'limited', 'full'}:
        raise ValueError('Invalid access mode.')
    SETTINGS_FILE.write_text(json.dumps({'access_mode': mode}, ensure_ascii=False, indent=2), encoding='utf-8')
    return mode

def _resolve_path(path: str = '.') -> Path:
    raw = Path(os.path.expandvars(os.path.expanduser(path)))
    if get_access_mode() == 'limited':
        target = (WORKSPACE / raw).resolve() if not raw.is_absolute() else raw.resolve()
        if target != WORKSPACE and WORKSPACE not in target.parents:
            raise PermissionError('Limited access is enabled. File operations are restricted to the NOVA workspace. Choose Full User Access in Settings to use other locations.')
        return target
    # Full means all paths permitted to the currently running Windows account, not elevation.
    if not raw.is_absolute():
        raw = Path.home() / raw
    return raw.resolve()

def create_folder(path: str):
    target = _resolve_path(path)
    target.mkdir(parents=True, exist_ok=True)
    return f'Folder created or already existed: {target}'

def create_file(path: str, content: str, overwrite: bool = False):
    target = _resolve_path(path)
    if target.exists() and not overwrite:
        return f'File already exists and was not overwritten: {target}. Only use overwrite=true when the user explicitly requests overwriting.'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')
    return f'File saved: {target}'

def read_file(path: str):
    target = _resolve_path(path)
    if not target.is_file():
        raise FileNotFoundError('File not found.')
    if target.stat().st_size > 1_000_000:
        raise ValueError('File exceeds the 1 MB reading limit.')
    return target.read_text(encoding='utf-8')

def list_directory(path: str = '.'):
    folder = _resolve_path(path)
    if not folder.is_dir():
        raise NotADirectoryError('The path is not a directory or does not exist.')
    entries = []
    for item in sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))[:200]:
        entries.append(('📁 ' if item.is_dir() else '📄 ') + item.name)
    return f'Contents of {folder}:\n' + ('\n'.join(entries) if entries else 'This folder is empty.')

def copy_path(source: str, destination: str):
    src, dst = _resolve_path(source), _resolve_path(destination)
    if not src.exists(): raise FileNotFoundError('Source path not found.')
    if dst.exists(): raise FileExistsError('Destination already exists. The operation was cancelled to avoid overwriting it.')
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
    return f'Copied: {src} -> {dst}'

def move_path(source: str, destination: str):
    src, dst = _resolve_path(source), _resolve_path(destination)
    if not src.exists(): raise FileNotFoundError('Source path not found.')
    if dst.exists(): raise FileExistsError('Destination already exists. The operation was cancelled.')
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return f'Moved: {src} -> {dst}'

def open_folder(path: str = '.'):
    target = _resolve_path(path)
    if not target.exists(): raise FileNotFoundError('Folder not found.')
    if not target.is_dir(): raise NotADirectoryError('The selected path is not a folder.')
    if os.name == 'nt': os.startfile(str(target))
    elif sys.platform == 'darwin': subprocess.Popen(['open', str(target)])
    else: subprocess.Popen(['xdg-open', str(target)])
    return f'Opened folder in the file manager: {target}'

def _find_application(app_name: str):
    name = app_name.strip().lower()
    aliases = {
        'chrome': ['chrome.exe'], 'google chrome': ['chrome.exe'], 'کروم': ['chrome.exe'],
        'edge': ['msedge.exe'], 'مایکروسافت اج': ['msedge.exe'],
        'firefox': ['firefox.exe'], 'فایرفاکس': ['firefox.exe'],
        'notepad': ['notepad.exe'], 'دفترچه یادداشت': ['notepad.exe'],
        'calculator': ['calc.exe'], 'ماشین حساب': ['calc.exe'], 'ماشین‌حساب': ['calc.exe'],
        'pycharm': ['pycharm64.exe'], 'پایچارم': ['pycharm64.exe'],
        'vscode': ['code.exe', 'code'], 'visual studio code': ['code.exe', 'code'],
    }
    exe_names = aliases.get(name, [app_name if app_name.lower().endswith('.exe') else app_name + '.exe'])
    for exe in exe_names:
        found = shutil.which(exe)
        if found: return found
    if os.name == 'nt':
        local = Path(os.environ.get('LOCALAPPDATA', ''))
        pf = Path(os.environ.get('PROGRAMFILES', r'C:\Program Files'))
        pfx86 = Path(os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)'))
        candidates = []
        if name in {'chrome','google chrome','کروم'}:
            candidates += [pf/'Google/Chrome/Application/chrome.exe', pfx86/'Google/Chrome/Application/chrome.exe', local/'Google/Chrome/Application/chrome.exe']
        if name in {'edge','مایکروسافت اج'}:
            candidates += [pf/'Microsoft/Edge/Application/msedge.exe', pfx86/'Microsoft/Edge/Application/msedge.exe']
        if name in {'firefox','فایرفاکس'}:
            candidates += [pf/'Mozilla Firefox/firefox.exe', pfx86/'Mozilla Firefox/firefox.exe']
        if name in {'pycharm','پایچارم'}:
            candidates += [pf/'JetBrains/PyCharm/bin/pycharm64.exe', pf/'JetBrains/PyCharm Community Edition/bin/pycharm64.exe']
            candidates += list((local/'Programs').glob('PyCharm*/bin/pycharm64.exe')) if (local/'Programs').exists() else []
        if name in {'vscode','visual studio code'}:
            candidates += [local/'Programs/Microsoft VS Code/Code.exe', pf/'Microsoft VS Code/Code.exe']
        for c in candidates:
            if c.is_file(): return str(c)
        # Search Start Menu shortcuts by display name, allowing other installed apps.
        starts = [Path(os.environ.get('APPDATA',''))/'Microsoft/Windows/Start Menu/Programs',
                  Path(os.environ.get('PROGRAMDATA',r'C:\ProgramData'))/'Microsoft/Windows/Start Menu/Programs']
        for root in starts:
            if root.exists():
                matches = [p for p in root.rglob('*.lnk') if name in p.stem.lower()]
                if matches: return str(matches[0])
    return None

def open_application(app_name: str):
    executable = _find_application(app_name)
    if not executable:
        raise FileNotFoundError(f'Application {app_name} was not found. Check the application name or executable path.')
    if os.name == 'nt' and executable.lower().endswith('.lnk'):
        os.startfile(executable)
    elif os.name == 'nt' and Path(executable).name.lower() in {'notepad.exe','calc.exe'}:
        subprocess.Popen([executable])
    else:
        subprocess.Popen([executable])
    return f'Launch request sent for: {app_name}'

def open_website(url: str):
    if not url.startswith(('https://', 'http://')): url = 'https://' + url
    webbrowser.open(url)
    return f'Opened website in the default browser: {url}'

def google_search(query: str):
    webbrowser.open('https://www.google.com/search?q=' + quote(query))
    return f'Opened Google search results for: {query}'


class _GoogleResultsParser(HTMLParser):
    """Extract organic result links from Google's server-rendered result page."""
    def __init__(self):
        super().__init__()
        self.results = []
        self.anchor_href = None
        self.anchor_depth = 0
        self.in_h3 = False
        self.title_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and self.anchor_href is None:
            self.anchor_href = attrs.get('href', '')
            self.anchor_depth = 1
        elif self.anchor_href is not None:
            self.anchor_depth += 1
        if tag == 'h3' and self.anchor_href is not None:
            self.in_h3 = True
            self.title_parts = []

    def handle_data(self, data):
        if self.in_h3:
            self.title_parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'h3' and self.in_h3:
            title = ' '.join(' '.join(self.title_parts).split())
            href = self.anchor_href or ''
            parsed = urlparse(href)
            if (parsed.netloc.endswith('google.com') or not parsed.netloc) and parsed.path == '/url':
                params = parse_qs(parsed.query)
                href = (params.get('q') or params.get('url') or [''])[0]
            if title and href.startswith(('http://', 'https://')):
                host = (urlparse(href).hostname or '').lower()
                if host and not (host == 'google.com' or host.endswith('.google.com')):
                    if not any(item['url'] == href for item in self.results):
                        self.results.append({'title': title, 'url': href})
            self.in_h3 = False
        if self.anchor_href is not None:
            self.anchor_depth -= 1
            if self.anchor_depth <= 0:
                self.anchor_href = None
                self.anchor_depth = 0
                self.in_h3 = False

def google_search_and_open(query: str, result_number: int = 2):
    """Open a numbered organic Google result (1 = first, 2 = second)."""
    if result_number < 1 or result_number > 10:
        raise ValueError('Result number must be between 1 and 10.')
    search_url = 'https://www.google.com/search?q=' + quote(query) + '&num=10'
    request = Request(search_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,*;q=0.5'
    })
    try:
        with urlopen(request, timeout=15) as response:
            html = response.read(3_000_000).decode('utf-8', errors='replace')
    except Exception as exc:
        webbrowser.open(search_url)
        return f'Could not retrieve Google results automatically ({exc}). Opened the Google results page instead; please choose result {result_number} manually.'
    parser = _GoogleResultsParser()
    parser.feed(html)
    if len(parser.results) < result_number:
        webbrowser.open(search_url)
        return f'Google returned too few readable organic results to identify result {result_number}. Opened the Google results page so you can select it manually.'
    result = parser.results[result_number - 1]
    webbrowser.open(result['url'])
    return f'Opened Google organic result #{result_number}: {result["title"]} ({result["url"]})'

def _tool(name, description, properties, required):
    return {'type':'function','function':{'name':name,'description':description,'parameters':{'type':'object','properties':properties,'required':required}}}

TOOLS = [
    _tool('create_folder','Create a folder at an absolute path or a path relative to the user home in full mode; in limited mode only inside workspace.',{'path':{'type':'string'}},['path']),
    _tool('create_file','Create a UTF-8 text or code file. Use an absolute path in full access mode. Never overwrite unless explicitly requested.',{'path':{'type':'string'},'content':{'type':'string'},'overwrite':{'type':'boolean'}},['path','content']),
    _tool('read_file','Read a UTF-8 text file at a permitted path.',{'path':{'type':'string'}},['path']),
    _tool('list_directory','List files and folders at a permitted directory path.',{'path':{'type':'string'}},[]),
    _tool('copy_path','Copy a file or folder to a destination that does not already exist.',{'source':{'type':'string'},'destination':{'type':'string'}},['source','destination']),
    _tool('move_path','Move a file or folder to a destination that does not already exist.',{'source':{'type':'string'},'destination':{'type':'string'}},['source','destination']),
    _tool('open_folder','Open a permitted folder in the operating system file manager.',{'path':{'type':'string'}},['path']),
    _tool('open_application','Launch an installed desktop application by its common name, e.g. Chrome, PyCharm, VS Code, Firefox.',{'app_name':{'type':'string'}},['app_name']),
    _tool('open_website','Open a website in the default browser.',{'url':{'type':'string'}},['url']),
    _tool('google_search','Open a Google search results page in the default browser.',{'query':{'type':'string'}},['query']),
    _tool('google_search_and_open','Search Google and open a numbered organic result. Use result_number=2 when the user asks for the second website/result.',{'query':{'type':'string'},'result_number':{'type':'integer','minimum':1,'maximum':10}},['query']),
]
FUNCTIONS = {f.__name__: f for f in [create_folder,create_file,read_file,list_directory,copy_path,move_path,open_folder,open_application,open_website,google_search,google_search_and_open]}
