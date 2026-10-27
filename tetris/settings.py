import json
from pathlib import Path


DEFAULT_PORT = 10000
SETTINGS_FILE = Path(__file__).resolve().parent.parent / 'data' / 'settings.json'


def load_port():
    try:
        settings = json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))
        port = settings.get('port') if isinstance(settings, dict) else None
        if type(port) is int and 1 <= port <= 65535:
            return port
    except (OSError, ValueError):
        pass
    return DEFAULT_PORT


def save_port(port):
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Informe uma porta entre 1 e 65535.')
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps({'port': port}, indent=2) + '\n', encoding='utf-8')
