#!/usr/bin/env python3

"""
Ingest Artifacts Script

Uploads artifacts to MinIO (S3) and records ZPDL metadata and SHA256 into Postgres.
Provides safe no-op if credentials are missing.

Requirements:
- Environment variables: DATABASE_URL, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
- Will not run automatically in CI - requires manual execution with proper credentials
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import boto3
    from botocore.exceptions import ClientError
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from app.core.database import SessionLocal
    from app.core.zpdl import generate_zpdl_metadata, sha256_hash
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Missing dependencies: {e}")
    DEPENDENCIES_AVAILABLE = False


class ArtifactIngestor:
    """Handles artifact upload to MinIO and metadata recording in Postgres."""
    
    def __init__(self):
        """Initialize with environment configuration."""
        self.minio_endpoint = os.getenv("MINIO_ENDPOINT")
        self.minio_access_key = os.getenv("MINIO_ACCESS_KEY")
        self.minio_secret_key = os.getenv("MINIO_SECRET_KEY")
        self.minio_bucket = os.getenv("MINIO_BUCKET", "zynx-artifacts")
        self.minio_use_ssl = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
        self.database_url = os.getenv("DATABASE_URL")
        
        self.s3_client = None
        self.db_session = None
        
    def check_credentials(self) -> bool:
        """Check if all required credentials are available."""
        missing = []
        
        if not self.minio_endpoint:
            missing.append("MINIO_ENDPOINT")
        if not self.minio_access_key:
            missing.append("MINIO_ACCESS_KEY")
        if not self.minio_secret_key:
            missing.append("MINIO_SECRET_KEY")
        if not self.database_url:
            missing.append("DATABASE_URL")
            
        if missing:
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            return False
            
        return True
    
    def connect(self) -> bool:
        """Connect to MinIO and database."""
        try:
            # Connect to MinIO
            self.s3_client = boto3.client(
                's3',
                endpoint_url=f"{'https' if self.minio_use_ssl else 'http'}://{self.minio_endpoint}",
                aws_access_key_id=self.minio_access_key,
                aws_secret_access_key=self.minio_secret_key,
                region_name='us-east-1'
            )
            
            # Test MinIO connection
            self.s3_client.head_bucket(Bucket=self.minio_bucket)
            print(f"✅ Connected to MinIO bucket: {self.minio_bucket}")
            
            # Connect to database
            self.db_session = SessionLocal()
            print("✅ Connected to PostgreSQL database")
            
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket doesn't exist, try to create it
                try:
                    self.s3_client.create_bucket(Bucket=self.minio_bucket)
                    print(f"✅ Created MinIO bucket: {self.minio_bucket}")
                    return True
                except Exception as create_error:
                    print(f"❌ Failed to create bucket: {create_error}")
                    return False
            else:
                print(f"❌ MinIO connection failed: {e}")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def ingest_file(self, file_path: str, artifact_type: str = "file") -> Optional[str]:
        """
        Ingest a single file to MinIO and record metadata.
        
        Args:
            file_path: Path to the file to ingest
            artifact_type: Type of artifact for metadata
            
        Returns:
            Object key if successful, None otherwise
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                return None
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Generate object key
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            object_key = f"{artifact_type}/{timestamp}_{file_path.name}"
            
            # Upload to MinIO
            self.s3_client.put_object(
                Bucket=self.minio_bucket,
                Key=object_key,
                Body=file_content,
                ContentType=self._get_content_type(file_path)
            )
            
            # Generate ZPDL metadata
            content_str = file_content.decode('utf-8', errors='ignore')
            metadata = generate_zpdl_metadata(
                content=content_str,
                artifact_type=artifact_type,
                additional_metadata={
                    "filename": file_path.name,
                    "file_size": len(file_content),
                    "object_key": object_key,
                    "bucket": self.minio_bucket
                }
            )
            
            # Record in database (simplified - would need proper table structure)
            try:
                # This is a simplified version - in production you'd have proper artifact tables
                self.db_session.execute(
                    text("""
                        INSERT INTO agent_manifests (agent_id, name, description, version, status, metadata)
                        VALUES (:agent_id, :name, :description, :version, :status, :metadata)
                        ON CONFLICT (agent_id) DO UPDATE SET
                            metadata = EXCLUDED.metadata,
                            updated_at = NOW()
                    """),
                    {
                        "agent_id": f"artifact_{metadata['sha256'][:8]}",
                        "name": f"Artifact: {file_path.name}",
                        "description": f"Ingested artifact: {file_path}",
                        "version": "1.0.0",
                        "status": "ingested",
                        "metadata": json.dumps(metadata)
                    }
                )
                self.db_session.commit()
            except Exception as db_error:
                print(f"⚠️  Database recording failed (continuing): {db_error}")
                self.db_session.rollback()
            
            print(f"✅ Ingested: {file_path.name} -> {object_key}")
            print(f"   SHA256: {metadata['sha256']}")
            
            return object_key
            
        except Exception as e:
            print(f"❌ Failed to ingest {file_path}: {e}")
            return None
    
    def _get_content_type(self, file_path: Path) -> str:
        """Get content type based on file extension."""
        extension = file_path.suffix.lower()
        content_types = {
            '.json': 'application/json',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.py': 'text/x-python',
            '.yml': 'text/yaml',
            '.yaml': 'text/yaml',
            '.sh': 'text/x-shellscript'
        }
        return content_types.get(extension, 'application/octet-stream')
    
    def close(self):
        """Close database connection."""
        if self.db_session:
            self.db_session.close()


def main():
    """Main function for command-line usage."""
    print("🔄 Zynx AGI - Artifact Ingestor")
    print("===============================")
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ Required dependencies not available. Install with:")
        print("   pip install boto3 sqlalchemy psycopg2-binary")
        sys.exit(1)
    
    ingestor = ArtifactIngestor()
    
    # Check credentials
    if not ingestor.check_credentials():
        print("\n⚠️  SAFE NO-OP: Missing credentials")
        print("This script requires environment variables to be set.")
        print("It will not run automatically in CI for security reasons.")
        print("\nRequired variables:")
        print("  - DATABASE_URL")
        print("  - MINIO_ENDPOINT")
        print("  - MINIO_ACCESS_KEY")
        print("  - MINIO_SECRET_KEY")
        print("  - MINIO_BUCKET (optional, defaults to 'zynx-artifacts')")
        sys.exit(0)  # Exit successfully for CI compatibility
    
    # Connect to services
    if not ingestor.connect():
        print("❌ Failed to connect to services")
        sys.exit(1)
    
    try:
        # If files are provided as arguments, ingest them
        if len(sys.argv) > 1:
            for file_path in sys.argv[1:]:
                ingestor.ingest_file(file_path)
        else:
            # Default: ingest some key files if they exist
            default_files = [
                "POST_MASTER.md",
                ".env.example",
                "README.md",
                "docker-compose.yml"
            ]
            
            print("No files specified, ingesting default files...")
            for file_path in default_files:
                if os.path.exists(file_path):
                    ingestor.ingest_file(file_path, "foundation")
        
        print("\n✅ Artifact ingestion completed")
        
    finally:
        ingestor.close()


if __name__ == "__main__":
    main()