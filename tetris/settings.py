import json
from pathlib import Path

from tetris.network.protocol import clean_name


DEFAULT_PORT = 10000
SETTINGS_FILE = Path(__file__).resolve().parent.parent / 'data' / 'settings.json'


def _load():
    try:
        settings = json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))
        return settings if isinstance(settings, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(key, value):
    settings = _load()
    settings[key] = value
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def load_port():
    port = _load().get('port')
    if type(port) is int and 1 <= port <= 65535:
        return port
    return DEFAULT_PORT


def save_port(port):
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Informe uma porta entre 1 e 65535.')
    _save('port', port)


def load_name():
    return clean_name(_load().get('name'))


def save_name(name):
    name = clean_name(name)
    if not name:
        raise ValueError('Informe um nome.')
    _save('name', name)
