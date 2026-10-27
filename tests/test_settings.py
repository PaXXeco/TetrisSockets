from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tetris import settings


class SettingsTests(unittest.TestCase):
    def test_port_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'data' / 'settings.json'
            with patch.object(settings, 'SETTINGS_FILE', path):
                self.assertEqual(settings.load_port(), settings.DEFAULT_PORT)
                for port in (1, 5000, 65535):
                    settings.save_port(port)
                    self.assertEqual(settings.load_port(), port)

    def test_invalid_ports_do_not_overwrite_saved_port(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(settings, 'SETTINGS_FILE', Path(directory) / 'settings.json'):
                settings.save_port(5000)
                for port in (0, -1, 65536, True, '5000'):
                    with self.subTest(port=port), self.assertRaises(ValueError):
                        settings.save_port(port)
                self.assertEqual(settings.load_port(), 5000)

    def test_invalid_file_falls_back_to_default(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'settings.json'
            with patch.object(settings, 'SETTINGS_FILE', path):
                for content in ('invalid', '[]', '{"port": 0}', '{"port": true}'):
                    path.write_text(content)
                    self.assertEqual(settings.load_port(), settings.DEFAULT_PORT)
