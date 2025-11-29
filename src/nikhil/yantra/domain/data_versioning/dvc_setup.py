# src/nikhil/yantra/domain/data_versioning/dvc_setup.py
import subprocess
import boto3
from pathlib import Path

from botocore.config import Config
from botocore.exceptions import ClientError

from yantra.utils import YamlUtils


# Define custom exceptions for the library
class YantraDVCError(Exception):
    """Base exception for Yantra DVC operations."""
    pass


class DVCSetup:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise YantraDVCError(f"Configuration file not found at: {self.config_path}")

        self.config = YamlUtils.yaml_safe_load(config_path)
        self.root_dir = Path.cwd()

        # Handle optional paths safely
        self.input_dir = Path(self.config.get("domain_root_path", "data/input"))
        self.output_dir = Path(self.config.get("output_dir_path", "data/output"))
        self.s3_config = self.config.get("s3_config")

    def _run_command(self, command: list, check=True):
        try:
            result = subprocess.run(
                command,
                check=check,
                text=True,
                cwd=self.root_dir,
                capture_output=True
            )
            return result
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {' '.join(command)}\nSTDERR: {e.stderr}"
            print(f"Error: {error_msg}")
            raise YantraDVCError(error_msg) from e

    def _create_directories(self):
        """MISSING METHOD RESTORED: Creates local input/output folders."""
        print("\nEnsuring local directories exist...")
        for dir_path in [self.input_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        print("   - Directories checked.")

    def _ensure_bucket_exists(self):
        print("\nVerifying S3 Bucket status...")
        bucket_name = self.s3_config["bucket_name"]

        s3_client = boto3.client(
            "s3",
            endpoint_url=self.s3_config.get("endpoint_url"),
            aws_access_key_id=self.s3_config["access_key_id"],
            aws_secret_access_key=self.s3_config["secret_access_key"],
            region_name=self.s3_config.get("region", "us-east-1"),
            use_ssl=self.s3_config.get("use_ssl", False),
            config=Config(s3={'addressing_style': 'path'})
        )

        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"   - Bucket '{bucket_name}' ready.")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"   - Bucket '{bucket_name}' not found. Creating...")
                try:
                    s3_client.create_bucket(Bucket=bucket_name)
                    print(f"   - Bucket created.")
                except Exception as create_err:
                    raise YantraDVCError(f"Failed to create bucket: {create_err}")
            elif error_code == '403':
                raise YantraDVCError(f"Access Denied to bucket '{bucket_name}'. Check credentials.")
            else:
                raise YantraDVCError(f"S3 Connection Error: {e}")

    def _configure_dvc(self):
        """Initializes DVC and sets remote."""
        print("\nConfiguring DVC for S3...")

        # 1. Initialize if not exists
        if not (self.root_dir / ".dvc").exists():
            self._run_command(["dvc", "init"])

        # 2. Configure Remote
        bucket_name = self.s3_config["bucket_name"]
        remote_url = f"s3://{bucket_name}/dvc_store"

        # Add Remote (Force overwrites if exists)
        self._run_command(["dvc", "remote", "add", "-d", "s3_storage", remote_url, "--force"])

        # 3. Modify Remote Settings
        endpoint_url = self.s3_config.get("endpoint_url")
        if endpoint_url:
            self._run_command(["dvc", "remote", "modify", "s3_storage", "endpointurl", endpoint_url])

        self._run_command(["dvc", "remote", "modify", "s3_storage", "use_ssl", "false"])

        # 4. Set Credentials (Local only)
        self._run_command(["dvc", "remote", "modify", "--local", "s3_storage",
                           "access_key_id", self.s3_config["access_key_id"]])
        self._run_command(["dvc", "remote", "modify", "--local", "s3_storage",
                           "secret_access_key", self.s3_config["secret_access_key"]])
        print("   - DVC remote configured.")

    def _bootstrap_data(self):

        print("\nAttempting to pull existing data...")
        self._run_command(["dvc", "pull"], check=False)

        # Track and Push
        print("\nTracking and Pushing local data...")
        self._run_command(["dvc", "add", str(self.input_dir)])
        self._run_command(["dvc", "add", str(self.output_dir)])

        self._run_command(["git", "add", ".gitignore", f"{self.input_dir}.dvc", f"{self.output_dir}.dvc"], check=False)
        self._run_command(["git", "commit", "-m", "chore: Initial DVC setup"], check=False)

        # Push to S3
        self._run_command(["dvc", "push"])
        print("   - Data pushed to MinIO successfully.")



    def setup(self):
        """
        Infrastructure ONLY setup.
        1. Create Directories
        2. Create S3 Buckets
        3. Init DVC & Config Remote
        """
        try:
            self._create_directories()
            self._ensure_bucket_exists()
            self._configure_dvc()
            self._bootstrap_data()
            print("\nDVC Environment Ready!")
        except YantraDVCError as e:
            print(f"\nSetup Failed: {e}")
            raise e