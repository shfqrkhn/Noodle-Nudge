
import re

def extract_urls(filepath, pattern):
    with open(filepath, 'r') as f:
        content = f.read()
    return re.findall(pattern, content)

def main():
    # Both use single quotes in the file content I read earlier
    index_pattern = r"'(https://raw\.githubusercontent\.com/shfqrkhn/Noodle-Nudge/[^']+)'"
    sw_pattern = r"'(https://raw\.githubusercontent\.com/shfqrkhn/Noodle-Nudge/[^']+)'"

    index_urls = extract_urls('docs/index.html', index_pattern)
    sw_urls = extract_urls('docs/service-worker.js', sw_pattern)

    print(f"Found {len(index_urls)} URLs in index.html")
    print(f"Found {len(sw_urls)} URLs in service-worker.js")

    mismatches = []
    # Normalize and compare filenames
    index_files = {url.split('/')[-1]: url for url in index_urls}
    sw_files = {url.split('/')[-1]: url for url in sw_urls}

    all_files = set(index_files.keys()) | set(sw_files.keys())

    for filename in all_files:
        i_url = index_files.get(filename)
        s_url = sw_files.get(filename)

        if i_url and s_url:
            if i_url != s_url:
                print(f"MISMATCH for {filename}:")
                print(f"  Index: {i_url}")
                print(f"  SW:    {s_url}")
                mismatches.append(filename)
        elif i_url:
             print(f"MISSING in SW: {filename}")
        else:
             print(f"MISSING in Index: {filename}")

    if mismatches:
        print(f"\nTotal Mismatches: {len(mismatches)}")
    else:
        print("\nNo mismatches found (if counts are > 0).")

if __name__ == "__main__":
    main()
