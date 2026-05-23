"""Extract file URIs from CERN records 30522 (Run2016G) and 30555 (Run2016H)."""
import json

def extract_files(path, label):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    i = text.find('{')
    data = json.loads(text[i:])
    meta = data.get('metadata', {})
    print(f"\n{'='*60}")
    print(f"  {label}: {meta.get('title', '?')}")
    
    fi_list = meta.get('_file_indices', [])
    if not fi_list:
        print("  No _file_indices!")
        return []
    
    files = fi_list[0].get('files', [])
    total_sz = sum(f.get('size', 0) for f in files)
    print(f"  Files: {len(files)}")
    print(f"  Total: {total_sz/1e9:.1f} GB")
    
    # Extract filenames from URIs
    result = []
    for f in files:
        uri = f.get('uri', '')
        size = f.get('size', 0)
        # Extract just the filename from root://eospublic.cern.ch//eos/opendata/...
        fname = uri.split('/')[-1]
        result.append((fname, size))
    
    # Sort by size for convenient batching
    result.sort(key=lambda x: x[1])
    
    print(f"\n  Files sorted by size:")
    for fname, sz in result:
        print(f'            "{fname}",   # {sz/1e9:.2f} GB')
    
    return result

# Run2016G (already have partial)
g_path = r"C:\Users\mail\.gemini\antigravity\brain\41c2c258-022b-4d46-84fe-cc5ad8f40ef7\.system_generated\steps\157\content.md"
g_files = extract_files(g_path, "Run2016G (Record 30522)")

# Run2016H 
h_path = r"C:\Users\mail\.gemini\antigravity\brain\41c2c258-022b-4d46-84fe-cc5ad8f40ef7\.system_generated\steps\278\content.md"
h_files = extract_files(h_path, "Run2016H (Record 30555)")

# Summary
g_total = sum(s for _, s in g_files)
h_total = sum(s for _, s in h_files)
print(f"\n{'='*60}")
print(f"  TOTAL: {len(g_files) + len(h_files)} files, {(g_total+h_total)/1e9:.1f} GB")
