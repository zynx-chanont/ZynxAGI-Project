#!/usr/bin/env python3

"""
Export Prompts Parser

Minimal parser that accepts a JSON file and writes out per-session JSON files.
Designed to process OpenAI conversation exports.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path


def parse_openai_export(input_file: str, output_dir: str) -> None:
    """
    Parse OpenAI exported JSON and create individual session files.
    
    Args:
        input_file: Path to input JSON file
        output_dir: Directory to save individual session files
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        sessions_count = 0
        
        # Handle different possible structures
        conversations = []
        
        if isinstance(data, list):
            conversations = data
        elif isinstance(data, dict):
            # Check common export formats
            if 'conversations' in data:
                conversations = data['conversations']
            elif 'data' in data:
                conversations = data['data']
            else:
                # Assume the dict itself is a conversation
                conversations = [data]
        
        for i, conversation in enumerate(conversations):
            # Generate session filename
            session_id = conversation.get('id', f'session_{i+1}')
            filename = f"session_{session_id}.json"
            filepath = os.path.join(output_dir, filename)
            
            # Create structured session data
            session_data = {
                "session_id": session_id,
                "exported_at": datetime.now().isoformat(),
                "source": "openai_export",
                "metadata": {
                    "title": conversation.get('title', f'Conversation {i+1}'),
                    "create_time": conversation.get('create_time'),
                    "update_time": conversation.get('update_time'),
                    "model": conversation.get('model')
                },
                "messages": [],
                "original_data": conversation
            }
            
            # Extract messages if available
            if 'mapping' in conversation:
                # OpenAI export format with message mapping
                mapping = conversation['mapping']
                for msg_id, msg_data in mapping.items():
                    if msg_data and 'message' in msg_data:
                        msg = msg_data['message']
                        if msg and 'content' in msg:
                            content = msg['content']
                            if content and 'parts' in content:
                                session_data['messages'].append({
                                    "id": msg_id,
                                    "role": msg.get('author', {}).get('role', 'unknown'),
                                    "content": ' '.join(content['parts']),
                                    "create_time": msg.get('create_time')
                                })
            
            elif 'messages' in conversation:
                # Direct messages format
                session_data['messages'] = conversation['messages']
            
            # Save session file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            sessions_count += 1
            print(f"📝 Exported: {filename}")
        
        print(f"\n✅ Successfully exported {sessions_count} sessions to {output_dir}")
        
    except FileNotFoundError:
        print(f"❌ Error: Input file '{input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in input file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: Failed to process file: {e}")
        sys.exit(1)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 3:
        print("Usage: python export_prompts_parser.py <input_file.json> <output_directory>")
        print("")
        print("This script parses OpenAI conversation exports and creates")
        print("individual JSON files for each session.")
        print("")
        print("Example:")
        print("  python export_prompts_parser.py conversations.json ./exported_sessions")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    print(f"🔄 Parsing OpenAI export: {input_file}")
    print(f"📁 Output directory: {output_dir}")
    print("")
    
    parse_openai_export(input_file, output_dir)


if __name__ == "__main__":
    main()