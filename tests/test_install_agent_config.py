import importlib.util
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "install_agent_config", ROOT / "scripts/install-agent-config.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class AgentConfigInstallTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.home = Path(self.directory.name)
        self.home_patch = patch.object(module, "HOME", self.home)
        self.home_patch.start()
        self.addCleanup(self.home_patch.stop)
        self.addCleanup(self.directory.cleanup)

    def test_fresh_install_has_codex_model_and_minimal_claude_settings(self):
        codex = self.home / ".codex/config.toml"
        codex.parent.mkdir()
        codex.write_text(
            '[mcp_servers.executor.http_headers]\nAuthorization = "Bearer test-token"\n'
        )

        token = module.install_codex()
        module.install_claude()
        module.install_claude_mcp(token)

        codex_settings = tomllib.loads(codex.read_text())
        claude_settings = json.loads((self.home / ".claude/settings.json").read_text())
        claude_mcp = json.loads((self.home / ".claude.json").read_text())
        self.assertEqual("gpt-6-sol", codex_settings["model"])
        self.assertEqual("high", codex_settings["model_reasoning_effort"])
        self.assertIn("paper", codex_settings["mcp_servers"])
        template = (ROOT / "dotfiles/agents/codex-config.toml.tmpl").read_text()
        self.assertEqual(
            template.replace(module.TOKEN_MARKER, 'Authorization = "Bearer test-token"'),
            codex.read_text(),
        )
        self.assertEqual(
            {"attribution", "enabledPlugins", "extraKnownMarketplaces"},
            set(claude_settings),
        )
        self.assertTrue(claude_settings["enabledPlugins"]["paper-desktop@paper"])
        self.assertIn("paper", claude_settings["extraKnownMarketplaces"])
        self.assertEqual("Bearer test-token", claude_mcp["mcpServers"]["executor"]["headers"]["Authorization"])

    def test_existing_claude_settings_are_reduced_and_install_is_idempotent(self):
        target = self.home / ".claude/settings.json"
        target.parent.mkdir()
        target.write_text(
            json.dumps(
                {
                    "autoMode": {"environment": {"local": "keep"}},
                    "enabledPlugins": {"local-plugin@custom": True},
                    "extraKnownMarketplaces": {"custom": {"source": "local"}},
                    "hooks": {"SessionStart": [{"command": "local-hook"}]},
                    "statusLine": {"command": "local-status"},
                }
            )
        )

        module.install_claude()
        installed = target.read_text()
        settings = json.loads(installed)
        self.assertEqual(
            {"attribution", "enabledPlugins", "extraKnownMarketplaces"},
            set(settings),
        )
        self.assertTrue(settings["enabledPlugins"]["paper-desktop@paper"])
        self.assertNotIn("custom", settings["extraKnownMarketplaces"])

        module.install_claude()
        self.assertEqual(installed, target.read_text())


if __name__ == "__main__":
    unittest.main()
