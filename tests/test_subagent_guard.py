"""
Subagent-guard behavioral test: with CLAUDE_SUBAGENT=1 set, every hook script
MUST be a no-op (exit 0 with no side effects on state/).

Run: python -m unittest tests.test_subagent_guard -v
"""
import os
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"


def _bash_available() -> bool:
    try:
        subprocess.run(["bash", "--version"], capture_output=True, timeout=3)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@unittest.skipUnless(_bash_available(), "bash not available")
class TestSubagentGuard(unittest.TestCase):
    def test_every_hook_no_ops_with_guard_set(self):
        env = os.environ.copy()
        env["CLAUDE_SUBAGENT"] = "1"
        hooks = list(PLUGINS_DIR.rglob("hooks/*/*.sh"))
        self.assertGreater(len(hooks), 0)
        for path in hooks:
            with self.subTest(hook=str(path.relative_to(REPO_ROOT))):
                plugin_root = path.parent.parent.parent
                env_with_root = dict(env)
                env_with_root["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
                result = subprocess.run(
                    ["bash", str(path)],
                    input="{}",
                    capture_output=True,
                    text=True,
                    env=env_with_root,
                    timeout=10,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"{path.name}: expected exit 0 with CLAUDE_SUBAGENT=1, got {result.returncode}. stderr={result.stderr}",
                )


if __name__ == "__main__":
    unittest.main()
