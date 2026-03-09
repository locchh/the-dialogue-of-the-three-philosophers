#!/usr/bin/env python3
"""
Script to create a chronological conversation timeline from agent conversation JSON export.
Organizes messages by timestamp across all agents.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def load_conversation_data(filepath: str) -> Dict[str, Any]:
    """Load conversation JSON data from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_all_messages(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all messages from all agents and combine them."""
    all_messages = []
    
    agents = data.get('agents', {})
    for agent_name, messages in agents.items():
        for msg in messages:
            msg_copy = msg.copy()
            msg_copy['agent'] = agent_name
            all_messages.append(msg_copy)
    
    return all_messages


def sort_messages_by_timestamp(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort messages chronologically by timestamp."""
    return sorted(messages, key=lambda x: datetime.fromisoformat(x['timestamp']))


def format_message_content(content: str, max_length: int = 200) -> str:
    """Format message content for display, truncating if needed."""
    content = content.replace('\n', ' ').strip()
    if len(content) > max_length:
        return content[:max_length] + '...'
    return content


def extract_user_message(content: str) -> str:
    """Extract user message from JSON-RPC formatted content if present."""
    try:
        data = json.loads(content)
        if 'params' in data and 'message' in data['params']:
            parts = data['params']['message'].get('parts', [])
            if parts and 'text' in parts[0]:
                return parts[0]['text']
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    return content


def create_timeline_text(messages: List[Dict[str, Any]]) -> str:
    """Create a formatted text timeline of the conversation."""
    lines = []
    lines.append("=" * 80)
    lines.append("CONVERSATION TIMELINE")
    lines.append("=" * 80)
    lines.append("")
    
    for i, msg in enumerate(messages, 1):
        timestamp = datetime.fromisoformat(msg['timestamp'])
        agent = msg['agent'].upper()
        direction = msg['direction']
        msg_type = msg['type']
        
        lines.append(f"[{i}] {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"    Agent: {agent}")
        lines.append(f"    Direction: {direction}")
        lines.append(f"    Type: {msg_type}")
        
        content = msg['content']
        if direction == 'incoming' and msg_type == 'agent_to_agent':
            content = extract_user_message(content)
        
        formatted_content = format_message_content(content, max_length=150)
        lines.append(f"    Content: {formatted_content}")
        lines.append("")
    
    return "\n".join(lines)


def create_timeline_markdown(messages: List[Dict[str, Any]], session_id: str) -> str:
    """Create a markdown formatted timeline of the conversation."""
    lines = []
    lines.append(f"# Conversation Timeline - Session {session_id}")
    lines.append("")
    lines.append(f"**Total Messages:** {len(messages)}")
    lines.append("")
    
    current_date = None
    
    for i, msg in enumerate(messages, 1):
        timestamp = datetime.fromisoformat(msg['timestamp'])
        msg_date = timestamp.strftime('%Y-%m-%d')
        
        if msg_date != current_date:
            current_date = msg_date
            lines.append(f"## {current_date}")
            lines.append("")
        
        agent = msg['agent'].capitalize()
        direction = "→" if msg['direction'] == 'outgoing' else "←"
        time_str = timestamp.strftime('%H:%M:%S')
        
        lines.append(f"### {direction} {time_str} - {agent}")
        lines.append("")
        
        content = msg['content']
        if msg['direction'] == 'incoming' and msg['type'] == 'agent_to_agent':
            content = extract_user_message(content)
        
        formatted_content = format_message_content(content, max_length=300)
        lines.append(f"> {formatted_content}")
        lines.append("")
    
    return "\n".join(lines)


def create_timeline_json(messages: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
    """Create a JSON formatted timeline with metadata."""
    timeline = {
        'metadata': metadata,
        'total_messages': len(messages),
        'timeline': []
    }
    
    for msg in messages:
        timeline_entry = {
            'timestamp': msg['timestamp'],
            'agent': msg['agent'],
            'direction': msg['direction'],
            'type': msg['type'],
            'content': msg['content']
        }
        
        if msg['direction'] == 'incoming' and msg['type'] == 'agent_to_agent':
            timeline_entry['extracted_message'] = extract_user_message(msg['content'])
        
        timeline['timeline'].append(timeline_entry)
    
    return json.dumps(timeline, indent=2, ensure_ascii=False)


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_conversation_timeline.py <input_json_file> [output_format]")
        print("  output_format: text (default), markdown, json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'text'
    
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    print(f"Loading conversation data from: {input_file}")
    data = load_conversation_data(input_file)
    
    session_id = data.get('session_id', 'unknown')
    exported_at = data.get('exported_at', 'unknown')
    
    print(f"Session ID: {session_id}")
    print(f"Exported at: {exported_at}")
    
    messages = extract_all_messages(data)
    print(f"Total messages found: {len(messages)}")
    
    sorted_messages = sort_messages_by_timestamp(messages)
    print("Sorting messages by timestamp...")
    
    input_path = Path(input_file)
    base_name = input_path.stem
    
    if output_format == 'markdown':
        output_file = input_path.parent / f"{base_name}_timeline.md"
        content = create_timeline_markdown(sorted_messages, session_id)
    elif output_format == 'json':
        output_file = input_path.parent / f"{base_name}_timeline.json"
        metadata = {
            'session_id': session_id,
            'exported_at': exported_at,
            'team_dir': data.get('team_dir', '')
        }
        content = create_timeline_json(sorted_messages, metadata)
    else:
        output_file = input_path.parent / f"{base_name}_timeline.txt"
        content = create_timeline_text(sorted_messages)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nTimeline created successfully: {output_file}")
    print(f"Format: {output_format}")


if __name__ == '__main__':
    main()
