# src/nikhil/yantra/domain/data_versioning/dvc_tracker.py
import subprocess
from pathlib import Path
from datetime import datetime

from nikhil.yantra.domain.data_versioning import IDataVersionControl
from nikhil.yantra.utils.yaml_utils import YamlUtils
from nikhil.yantra.domain.data_versioning.dvc_setup import DVCSetup, YantraDVCError


class DVCDataTracker(IDataVersionControl):
    """
    Production implementation of IDataVersionControl.
    Adheres strictly to the Protocol.
    """

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise YantraDVCError(f"Config not found: {self.config_path}")

        self.config = YamlUtils.yaml_safe_load(config_path)
        self.root_dir = Path.cwd()
        self.input_dir = Path(self.config.get("domain_root_path", "data/input"))
        self.output_dir = Path(self.config.get("output_dir_path", "data/output"))
        self.commit_msg = self.config.get("commit_message", "Auto-sync data")

    def _run_command(self, command: list, check=True):
        try:
            # Helper to run shell commands quietly
            return subprocess.run(
                command, check=check, text=True, cwd=self.root_dir, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            raise YantraDVCError(f"DVC Error: {e.stderr.strip()}") from e

    # --- Protocol Implementation ---

    def setup(self) -> None:
        """
        Adheres to IDataVersionControl.setup().
        Delegates to DVCSetup class to keep concerns separated.
        """
        print("Delegating setup to DVCSetup...")
        initializer = DVCSetup(str(self.config_path))
        initializer.setup()

    def pull(self) -> None:
        print("Pulling data...")
        # Check if DVC is initialized first
        if not (self.root_dir / ".dvc").exists():
            print("   DVC not init, skipping pull.")
            return
        self._run_command(["dvc", "pull"], check=False)

    def track(self, path: Path = None) -> None:
        print("Tracking data...")
        target = path if path else self.input_dir

        # FIX: Ensure directory exists before tracking to prevent crash
        if not target.exists():
            print(f"   Target {target} does not exist. Creating empty placeholder...")
            target.mkdir(parents=True, exist_ok=True)
            # Create a .gitkeep so DVC/Git has something to see
            (target / ".gitkeep").touch()

        self._run_command(["dvc", "add", str(target)])

    def push(self) -> None:
        print("Pushing data...")
        self._run_command(["dvc", "push"])

    def sync(self) -> None:
        """
        Full workflow: Pull -> Track -> Git Commit -> Push
        """
        self.pull()

        # Track input and output specifically
        self.track(self.input_dir)
        self.track(self.output_dir)

        # Git Commit Logic
        status = self._run_command(["git", "status", "--porcelain"])
        if ".dvc" in status.stdout:
            print("Committing DVC changes to Git...")
            self._run_command(["git", "add", "*.dvc", ".gitignore"])

            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            self._run_command(["git", "commit", "-m", f"{self.commit_msg} ({ts})"])

        self.push()