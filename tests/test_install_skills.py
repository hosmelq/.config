import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("install_skills", ROOT / "scripts/install-skills.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class SkillsInstallTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.home = Path(directory.name)
        self.manifest = self.home / "repo-lock.json"
        self.manifest.write_text(json.dumps({"version": 3, "skills": {
            name: {"sourceUrl": "https://github.com/example/skills.git", "sourceType": "github"}
            for name in ["existing", "missing"]
        }}))
        lock = self.home / ".agents/.skill-lock.json"
        lock.parent.mkdir()
        lock.symlink_to(self.manifest)
        self.write_skill("existing", "keep local content")
        self.write_skill("untracked", "keep independent skill")
        (self.home / ".agents/.skill-install-state.json").write_text(json.dumps({
            "existing": module.source_identity(json.loads(self.manifest.read_text())["skills"]["existing"])
        }))
        self.commands = []
        for name, value in [("HOME", self.home), ("MANIFEST", self.manifest)]:
            context = patch.object(module, name, value)
            context.start()
            self.addCleanup(context.stop)

    def write_skill(self, name, content):
        path = self.home / ".agents/skills" / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def cli(self, command, **options):
        self.commands.append(command)
        self.assertTrue(options["check"])
        self.assertNotIn("XDG_STATE_HOME", options["env"])
        if "add" in command:
            for name in command[command.index("--skill") + 1:]:
                self.write_skill(name, "restored")
        else:
            data = json.loads(self.manifest.read_text())
            data["skills"]["existing"]["updatedAt"] = "updated by CLI"
            (self.home / ".agents/.skill-lock.json").write_text(json.dumps(data))

    def test_restore_and_update_preserve_independent_skills_and_lock_link(self):
        with patch.object(module.subprocess, "run", side_effect=self.cli):
            module.install()
            module.install()
        self.assertEqual(1, sum("add" in command for command in self.commands))
        self.assertEqual(["missing"], self.commands[0][self.commands[0].index("--skill") + 1:])
        self.assertIn("--global", self.commands[1])
        self.assertTrue((self.home / ".agents/.skill-lock.json").is_symlink())
        self.assertIn("updatedAt", json.loads(self.manifest.read_text())["skills"]["existing"])
        self.assertEqual("keep independent skill", (self.home / ".agents/skills/untracked/SKILL.md").read_text())

    def test_new_repository_lock_reinstalls_existing_files_on_other_machine(self):
        self.write_skill("missing", "old version")
        data = json.loads(self.manifest.read_text())
        data["skills"]["existing"]["skillFolderHash"] = "new-upstream-version"
        self.manifest.write_text(json.dumps(data))
        with patch.object(module.subprocess, "run", side_effect=self.cli):
            module.install()
        self.assertEqual("restored", (self.home / ".agents/skills/existing/SKILL.md").read_text())
        state = json.loads((self.home / ".agents/.skill-install-state.json").read_text())
        self.assertEqual("new-upstream-version", state["existing"]["skillFolderHash"])

    def test_successful_cli_that_does_not_restore_skill_is_an_error(self):
        with patch.object(module.subprocess, "run"):
            with self.assertRaisesRegex(RuntimeError, "Skills were not installed: missing"):
                module.install()

    def test_failed_install_stops_before_update(self):
        with patch.object(module.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "nubx")) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                module.install()
        self.assertEqual(1, run.call_count)


if __name__ == "__main__":
    unittest.main()
