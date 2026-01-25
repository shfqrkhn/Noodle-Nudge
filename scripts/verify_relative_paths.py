
import re
import sys

def extract_urls(filepath, pattern):
    with open(filepath, 'r') as f:
        content = f.read()
    return re.findall(pattern, content)

def check_absolute_urls(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    absolute_pattern = r'https://raw\.githubusercontent\.com/shfqrkhn/Noodle-Nudge/'
    matches = re.findall(absolute_pattern, content)
    return len(matches)

def main():
    print("Verifying relative paths and consistency...")

    # Pattern for relative JSON paths: starts with ./JSON/ and ends with .json
    # It catches both single and double quotes contexts roughly
    # In index.html: './JSON/...'
    # In service-worker.js: './JSON/...'
    relative_pattern = r"['\"](\./JSON/[^'\"]+\.json)['\"]"

    index_abs_count = check_absolute_urls('docs/index.html')
    sw_abs_count = check_absolute_urls('docs/service-worker.js')

    if index_abs_count > 0:
        print(f"FAILURE: Found {index_abs_count} absolute URLs in docs/index.html")
    if sw_abs_count > 0:
        print(f"FAILURE: Found {sw_abs_count} absolute URLs in docs/service-worker.js")

    if index_abs_count > 0 or sw_abs_count > 0:
        sys.exit(1)

    index_urls = extract_urls('docs/index.html', relative_pattern)
    sw_urls = extract_urls('docs/service-worker.js', relative_pattern)

    print(f"Found {len(index_urls)} relative URLs in index.html")
    print(f"Found {len(sw_urls)} relative URLs in service-worker.js")

    if len(index_urls) == 0:
        print("FAILURE: No relative URLs found in index.html. Did replacements happen?")
        sys.exit(1)

    if len(sw_urls) == 0:
        print("FAILURE: No relative URLs found in service-worker.js. Did replacements happen?")
        sys.exit(1)

    index_set = set(index_urls)
    sw_set = set(sw_urls)

    if index_set != sw_set:
        print("FAILURE: URL sets do not match!")
        print(f"In Index but not SW: {index_set - sw_set}")
        print(f"In SW but not Index: {sw_set - index_set}")
        sys.exit(1)

    print("SUCCESS: Relative paths are consistent and absolute URLs are removed.")

if __name__ == "__main__":
    main()
