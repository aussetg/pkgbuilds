import json
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path


CONFIG = Path(__file__).resolve().parents[2] / "nvchecker.toml"


class NvcheckerConfigTests(unittest.TestCase):
    def setUp(self):
        self.config = tomllib.loads(CONFIG.read_text())

    def test_all_package_tables_have_sources(self):
        for name, entry in self.config.items():
            if not name.startswith("__"):
                with self.subTest(name=name):
                    self.assertIn("source", entry)

    def test_dotted_package_name_is_not_a_nested_table(self):
        self.assertEqual(self.config["swift-6.2-bin"]["source"], "manual")
        self.assertNotIn("swift-6", self.config)

    @unittest.skipUnless(shutil.which("nvchecker"), "nvchecker is not on PATH")
    def test_swift_tags_become_valid_pkgvers(self):
        entry = self.config["swift-bin"]
        for version in ("6.4.2", "6.5"):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                # Exercise nvchecker's real transformations without network access.
                config = (
                    '[__config__]\noldver = "old.json"\nnewver = "new.json"\n'
                    '[swift-bin]\nsource = "manual"\n'
                    f'manual = "swift-{version}-RELEASE"\n'
                )
                for key in ("prefix", "from_pattern", "to_pattern"):
                    if key in entry:
                        config += f"{key} = {json.dumps(entry[key])}\n"
                (root / "nvchecker.toml").write_text(config)
                result = subprocess.run(
                    ["nvchecker", "--failures", "-c", "nvchecker.toml"],
                    cwd=root, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                data = json.loads((root / "new.json").read_text())
                self.assertEqual(data["data"]["swift-bin"]["version"], version)


if __name__ == "__main__":
    unittest.main()
