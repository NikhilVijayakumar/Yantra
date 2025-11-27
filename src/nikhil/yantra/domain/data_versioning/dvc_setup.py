# src/nikhil/yantra/domain/data_versioning/dvc_setup.py
import subprocess
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from pathlib import Path
from nikhil.yantra.utils.yaml_utils import YamlUtils


# Define custom exceptions for the library
class YantraDVCError(Exception):
    """Base exception for Yantra DVC operations."""
    pass


class DVCSetup:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            # FIX 1: Raise exception instead of exit(1)
            raise YantraDVCError(f"Configuration file not found at: {self.config_path}")

        self.config = YamlUtils.yaml_safe_load(config_path)
        self.root_dir = Path.cwd()
        # Handle optional paths safely
        self.input_dir = Path(self.config.get("domain_root_path", "data/input"))
        self.output_dir = Path(self.config.get("output_dir_path", "data/output"))
        self.s3_config = self.config.get("s3_config")

    def _run_command(self, command: list, check=True):
        try:
            # FIX 2: Simplified subprocess handling
            result = subprocess.run(
                command,
                check=check,
                text=True,
                cwd=self.root_dir,
                capture_output=True
            )
            # Only print stdout if needed, ignore stderr unless it's an error
            # (handled by check=True)
            return result
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {' '.join(command)}.nSTDERR: {e.stderr}"
            print(f"❌ {error_msg}")
            # Re-raise as library specific error
            raise YantraDVCError(error_msg) from e

    def _ensure_bucket_exists(self):
        """Checks and creates S3 bucket using Boto3."""
        print(".n🪣  Verifying S3 Bucket status...")
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
            print(f"   - ✅ Bucket '{bucket_name}' ready.")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"   - ⚠️ Bucket '{bucket_name}' not found. Creating...")
                try:
                    s3_client.create_bucket(Bucket=bucket_name)
                    print(f"   - ✅ Bucket created.")
                except Exception as create_err:
                    raise YantraDVCError(f"Failed to create bucket: {create_err}")
            elif error_code == '403':
                raise YantraDVCError(f"Access Denied to bucket '{bucket_name}'. Check credentials.")
            else:
                raise YantraDVCError(f"S3 Connection Error: {e}")

    def setup(self):
        try:
            self._create_directories()
            self._ensure_bucket_exists()
            self._configure_dvc()
            self._bootstrap_data()
            print(".n🎉 Setup complete!")
        except YantraDVCError as e:
            print(f".n❌ Setup Failed: {e}")
            # Re-raise if you want the calling script to handle it
            raise e