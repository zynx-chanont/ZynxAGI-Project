#!/usr/bin/env python3

"""
Export Prompts Script
Simple script to help export/parse OpenAI session exports
"""

import sys
import os
from pathlib import Path


def main():
    """Main function for export prompts script."""
    print("🔄 Zynx AGI - Export Prompts Tool")
    print("==================================")

    # Check if input file is provided
    if len(sys.argv) < 2:
        print("Usage: python export_prompts.sh <input_file.json>")
        print("")
        print("This script parses OpenAI exported conversations and extracts")
        print("them into individual session files for analysis.")
        print("")
        print("Example:")
        print("  python export_prompts.sh conversations.json")
        print("")
        sys.exit(1)

    input_file = sys.argv[1]

    # Check if file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' not found")
        sys.exit(1)

    # Create output directory
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"exported_sessions_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"📄 Processing: {input_file}")
    print(f"📁 Output directory: {output_dir}")

    # Run the Python parser
    try:
        from export_prompts_parser import parse_openai_export
        parse_openai_export(input_file, output_dir)
        
        print("✅ Export completed successfully!")
        print(f"📊 Results saved in: {output_dir}")
        print("")
        print("📋 Summary:")
        
        # Count files in output directory
        files = list(Path(output_dir).glob("*.json"))
        print(f"   Sessions exported: {len(files)}")
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in files)
        size_mb = total_size / (1024 * 1024)
        print(f"   Total size: {size_mb:.2f} MB")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()