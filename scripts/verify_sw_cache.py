import os, re, sys
from urllib.parse import unquote

def run():
    try:
        with open('docs/service-worker.js', 'r', encoding='utf-8') as f: sw = f.read()
        match = re.search(r'const CONTENT_URLS = \[([\s\S]*?)\];', sw)
        if not match: raise Exception("CONTENT_URLS not found")

        # Parse URLs: remove whitespace, commas, quotes
        urls = [line.strip().strip("',\"") for line in match.group(1).split('\n') if line.strip()]
        sw_files = {unquote(u.replace('./JSON/', '')) for u in urls if './JSON/' in u}

        disk_files = {f for f in os.listdir('docs/JSON/') if f.endswith('.json')}

        missing_sw = disk_files - sw_files
        missing_disk = sw_files - disk_files

        if missing_sw or missing_disk:
            if missing_sw: print(f"❌ Missing in SW: {missing_sw}")
            if missing_disk: print(f"❌ Missing on Disk: {missing_disk}")
            sys.exit(1)

        print(f"✅ SUCCESS: Cache synced ({len(sw_files)} files).")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__": run()
