"""Extract all user messages from conversation transcript."""
import json

with open(r'C:\Users\mail\.gemini\antigravity\brain\98d55f1b-4a04-4215-908b-4e6af9ef9879\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total transcript lines: {len(lines)}")
print()

user_msgs = []
for line in lines:
    try:
        obj = json.loads(line.strip())
        if obj.get('type') == 'USER_INPUT' and obj.get('content'):
            content = obj['content'].strip()
            # Remove metadata
            if '<USER_REQUEST>' in content:
                import re
                m = re.search(r'<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>', content, re.DOTALL)
                if m:
                    content = m.group(1).strip()
            if content and len(content) > 2:
                user_msgs.append(content[:300])
    except:
        pass

print(f"User messages found: {len(user_msgs)}")
print("="*80)
for i, msg in enumerate(user_msgs, 1):
    print(f"\n[{i:2d}] {msg}")
