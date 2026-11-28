from pathlib import Path
from io import BytesIO
import base64
import ipaddress
import socket
import threading
import webbrowser

import qrcode
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field
from config import API_KEY, HOST, PORT
from ai import ask
from tools import get_access_mode, set_access_mode

BASE = Path(__file__).resolve().parent
WEB = BASE / 'web'
app = FastAPI(title='NOVA Desktop Assistant', docs_url=None, redoc_url=None)


class ChatRequest(BaseModel):
    messages: list[dict] = Field(default_factory=list)


def get_lan_addresses():
    """Return likely private LAN IPv4 addresses for phone access."""
    candidates = []
    try:
        for item in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            candidates.append(item[4][0])
    except OSError:
        pass
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(('8.8.8.8', 80))
        candidates.append(probe.getsockname()[0])
        probe.close()
    except OSError:
        pass

    result = []
    for address in candidates:
        try:
            ip = ipaddress.ip_address(address)
            if ip.version == 4 and ip.is_private and not ip.is_loopback and not ip.is_link_local:
                if address not in result:
                    result.append(address)
        except ValueError:
            continue
    return result


def make_qr_data_url(value: str) -> str:
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=3)
    qr.add_data(value)
    qr.make(fit=True)
    image = qr.make_image(fill_color='#07110d', back_color='white')
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    return f'data:image/png;base64,{encoded}'


@app.get('/', response_class=HTMLResponse)
def home():
    return (WEB / 'index.html').read_text(encoding='utf-8')


@app.get('/connect', response_class=HTMLResponse)
def connect_page():
    addresses = get_lan_addresses()
    cards = []
    if addresses:
        for address in addresses:
            url = f'http://{address}:{PORT}/'
            qr_src = make_qr_data_url(url)
            cards.append(
                '<article class="device-card">'
                f'<img src="{qr_src}" alt="QR code for {url}">'
                '<div class="device-info"><span class="eyebrow">PHONE ACCESS ADDRESS</span>'
                f'<a href="{url}">{url}</a>'
                f'<button onclick="copyAddress(\'{url}\')">Copy address</button>'
                '</div></article>'
            )
        cards_html = ''.join(cards)
        note = 'Make sure your phone and computer are connected to the same Wi-Fi network.'
    else:
        cards_html = '<div class="no-network">No local network address was detected. Connect this computer to Wi-Fi or Ethernet, then restart NOVA.</div>'
        note = 'You can still use NOVA on this computer at the local address below.'

    local_url = f'http://127.0.0.1:{PORT}/'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#08100d"><title>Connect to NOVA</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;padding:32px 16px;display:grid;place-items:center;background:radial-gradient(ellipse at 50% 0%,#17432e 0,transparent 48%),#080d0c;color:#edf7f1;font-family:Inter,Segoe UI,Arial,sans-serif}}main{{width:min(760px,100%);padding:clamp(22px,5vw,42px);border:1px solid #244333;border-radius:26px;background:#0d1712;box-shadow:0 24px 80px #0008}}.brand{{font-size:13px;letter-spacing:5px;color:#55d99b;font-weight:800}}h1{{font-size:clamp(25px,5vw,36px);margin:12px 0 8px}}p{{color:#9bb0a3;line-height:1.7;font-size:14px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin:26px 0}}.device-card{{display:flex;align-items:center;gap:15px;padding:14px;border:1px solid #294337;border-radius:18px;background:#101d16}}img{{width:132px;height:132px;border-radius:10px;background:#fff}}.device-info{{min-width:0;display:flex;flex-direction:column;gap:10px}}.eyebrow{{font-size:9px;letter-spacing:1.5px;color:#6edba6}}a{{color:#e4f7eb;overflow-wrap:anywhere;font-size:13px}}button{{border:0;border-radius:10px;padding:10px 13px;background:#25a96e;color:#fff;font-weight:700;font-size:12px;cursor:pointer;width:max-content}}.local{{padding:14px 16px;border:1px solid #263d31;border-radius:14px;background:#0a120e}}.local code{{color:#75e3aa;overflow-wrap:anywhere}}.note{{font-size:12px}}.no-network{{padding:18px;border:1px solid #704f35;border-radius:14px;color:#f0c99d;background:#24190f}}footer{{margin-top:22px;text-align:center;color:#62776b;font-size:11px}}@media(max-width:420px){{.device-card{{flex-direction:column;text-align:center}}.device-info{{align-items:center}}img{{width:150px;height:150px}}}}
</style></head><body><main><div class="brand">NOVA</div><h1>Connect your phone to NOVA</h1>
<p>Scan one of the QR codes below with your phone camera to open NOVA. Or enter the address manually in your mobile browser.</p>
<section class="cards">{cards_html}</section><p class="note">{note}</p>
<div class="local"><p style="margin:0 0 7px">Open NOVA on this computer:</p><a href="{local_url}"><code>{local_url}</code></a></div>
<footer>Developed by Mohammad Taha Torabzadeh</footer></main>
<script>function copyAddress(value){{if(navigator.clipboard){{navigator.clipboard.writeText(value).then(()=>alert('Address copied.')).catch(()=>alert(value));}}else{{alert(value);}}}}</script></body></html>'''


@app.get('/style.css')
def style():
    return Response((WEB / 'style.css').read_text(encoding='utf-8'), media_type='text/css')


@app.get('/app.js')
def script():
    return Response((WEB / 'app.js').read_text(encoding='utf-8'), media_type='application/javascript')


class AccessRequest(BaseModel):
    mode: str


@app.get('/api/settings/access')
def access_settings():
    return {'mode': get_access_mode()}


@app.post('/api/settings/access')
def update_access_settings(body: AccessRequest):
    try:
        mode = set_access_mode(body.mode)
        return {'mode': mode}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get('/health')
def health():
    return {'status': 'ok', 'api_configured': bool(API_KEY and API_KEY != 'PASTE_YOUR_KEY_HERE')}


@app.post('/api/chat')
def chat(body: ChatRequest):
    if not API_KEY or API_KEY == 'PASTE_YOUR_KEY_HERE':
        raise HTTPException(status_code=400, detail='OpenRouter API key is not configured in the .env file.')
    try:
        answer, history, model_info = ask(body.messages)
        return {'answer': answer, 'messages': history, **model_info}
    except Exception as exc:
        print('NOVA API ERROR:', repr(exc))
        response = getattr(exc, 'response', None)
        if response is not None:
            try:
                print('PROVIDER STATUS:', response.status_code)
                print('PROVIDER DETAILS:', response.text)
            except Exception:
                pass
        raise HTTPException(status_code=502, detail='Could not connect to the AI service. Check your internet connection, VPN, and API settings.')


if __name__ == '__main__':
    import uvicorn
    connect_url = f'http://127.0.0.1:{PORT}/connect'
    print('\n' + '=' * 58)
    print('NOVA is starting...')
    print('A phone connection page with QR code will open shortly.')
    print(f'If it does not open, visit: {connect_url}')
    print('=' * 58 + '\n')
    threading.Timer(1.5, lambda: webbrowser.open(connect_url)).start()
    uvicorn.run('main:app', host=HOST, port=PORT, reload=False)
