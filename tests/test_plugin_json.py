"""
Every .claude-plugin/plugin.json parses + has required keys.

Run: python -m unittest tests.test_plugin_json -v
"""
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

REQUIRED_KEYS = {"name", "version", "description"}
EXPECTED_PLUGINS = {
    "intent-anchor",
    "drift-aligner",
    "compact-guard",
    "utterance-rank",
    "drift-learning",
    "intent-reorient",
    "full",
}


class TestPluginJsonShape(unittest.TestCase):
    def test_all_expected_plugins_present(self):
        dirs = {p.name for p in PLUGINS_DIR.iterdir() if p.is_dir()}
        self.assertEqual(
            dirs,
            EXPECTED_PLUGINS,
            f"plugins/ directory set mismatch: unexpected={dirs - EXPECTED_PLUGINS} "
            f"missing={EXPECTED_PLUGINS - dirs}",
        )

    def test_every_plugin_json_parses_and_has_required_keys(self):
        for plugin_name in EXPECTED_PLUGINS:
            with self.subTest(plugin=plugin_name):
                path = PLUGINS_DIR / plugin_name / ".claude-plugin" / "plugin.json"
                self.assertTrue(path.exists(), f"{path} missing")
                data = json.loads(path.read_text(encoding="utf-8"))
                missing = REQUIRED_KEYS - data.keys()
                self.assertFalse(missing, f"{plugin_name}: missing keys {missing}")
                for key in REQUIRED_KEYS:
                    self.assertTrue(
                        str(data[key]).strip(),
                        f"{plugin_name}: key '{key}' is empty",
                    )

    def test_marketplace_json_lists_all_plugins(self):
        mp = REPO_ROOT / ".claude-plugin" / "marketplace.json"
        self.assertTrue(mp.exists())
        data = json.loads(mp.read_text(encoding="utf-8"))
        listed = {p["name"] for p in data["plugins"]}
        self.assertEqual(listed, EXPECTED_PLUGINS)


if __name__ == "__main__":
    unittest.main()
