import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("update-package.sh")
BASH = shutil.which("bash") or "/bin/bash"


class UpdatePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scripts = self.root / ".github" / "scripts"
        self.scripts.mkdir(parents=True)
        shutil.copy2(SCRIPT, self.scripts / SCRIPT.name)
        self.package = self.root / "example"
        self.package.mkdir()
        self.recipe = self.package / "PKGBUILD"
        self.srcinfo = self.package / ".SRCINFO"
        self.original = b"pkgname=example\npkgver=1.0\npkgrel=3\n# checksum\n"
        self.recipe.write_bytes(self.original)
        self.srcinfo.write_bytes(b"original metadata\n")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.command("updpkgsums", "printf '# refreshed\\n' >> PKGBUILD\n")
        self.command("makepkg", "printf 'updated metadata\\n'\n")
        # run_cmd uses login shells; set the test PATH after their startup files.
        startup = self.root / "bash-env"
        startup.write_text('export PATH="$TEST_BIN:$PATH"\n')
        self.env = {
            **os.environ,
            "BASH_ENV": str(startup),
            "TEST_BIN": str(self.bin),
        }

    def command(self, name, body):
        path = self.bin / name
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(0o755)

    def update(self, version="2.0"):
        return subprocess.run(
            [BASH, str(self.scripts / SCRIPT.name), "example", version],
            env=self.env, capture_output=True, text=True,
        )

    def assert_restored(self):
        self.assertEqual(self.recipe.read_bytes(), self.original)
        self.assertEqual(self.srcinfo.read_bytes(), b"original metadata\n")

    def test_success_keeps_updated_files(self):
        result = self.update()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"pkgver=2.0\npkgrel=1\n", self.recipe.read_bytes())
        self.assertIn(b"# refreshed\n", self.recipe.read_bytes())
        self.assertEqual(self.srcinfo.read_bytes(), b"updated metadata\n")

    def test_checksum_failure_restores_files(self):
        self.command("updpkgsums", "printf 'partial recipe\\n' > PKGBUILD\nexit 1\n")
        self.assertNotEqual(self.update().returncode, 0)
        self.assert_restored()

    def test_srcinfo_failure_restores_files(self):
        self.command("makepkg", "printf 'partial metadata\\n'\nexit 1\n")
        self.assertNotEqual(self.update().returncode, 0)
        self.assert_restored()

    def test_failure_removes_new_srcinfo(self):
        self.srcinfo.unlink()
        self.command("makepkg", "printf 'partial metadata\\n'\nexit 1\n")
        self.assertNotEqual(self.update().returncode, 0)
        self.assertEqual(self.recipe.read_bytes(), self.original)
        self.assertFalse(self.srcinfo.exists())

    def test_custom_updater_failure_restores_files(self):
        (self.scripts / "update-example.sh").write_text(
            '#!/bin/bash\nprintf "partial recipe\\n" > "$1/PKGBUILD"\nexit 1\n'
        )
        self.assertNotEqual(self.update().returncode, 0)
        self.assert_restored()

    def test_invalid_pkgver_is_rejected_before_editing(self):
        for version in ("", "6.4.2-RELEASE", "1:2", "1/2", "1 2", "1\n2"):
            with self.subTest(version=version):
                result = self.update(version)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("invalid pkgver", result.stderr)
                self.assert_restored()


if __name__ == "__main__":
    unittest.main()
