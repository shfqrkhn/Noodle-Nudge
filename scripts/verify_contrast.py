import re
import sys

def get_luminance(r, g, b):
    # Convert 0-255 to 0-1
    rs = r / 255.0
    gs = g / 255.0
    bs = b / 255.0

    # Linearize
    r_lin = rs / 12.92 if rs <= 0.03928 else ((rs + 0.055) / 1.055) ** 2.4
    g_lin = gs / 12.92 if gs <= 0.03928 else ((gs + 0.055) / 1.055) ** 2.4
    b_lin = bs / 12.92 if bs <= 0.03928 else ((bs + 0.055) / 1.055) ** 2.4

    # Calculate Y
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

def get_contrast_ratio(lum1, lum2):
    l1 = max(lum1, lum2)
    l2 = min(lum1, lum2)
    return (l1 + 0.05) / (l2 + 0.05)

def main():
    try:
        with open('docs/index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract --bs-primary-rgb
        match = re.search(r'--bs-primary-rgb:\s*(\d+),\s*(\d+),\s*(\d+);', content)
        if not match:
            print("FAILURE: Could not find --bs-primary-rgb definition.")
            sys.exit(1)

        r, g, b = map(int, match.groups())
        print(f"Found Primary Color RGB: {r}, {g}, {b}")

        lum_primary = get_luminance(r, g, b)
        lum_white = get_luminance(255, 255, 255) # White

        ratio = get_contrast_ratio(lum_primary, lum_white)
        print(f"Contrast Ratio against White: {ratio:.2f}:1")

        if ratio < 4.5:
            print("FAILURE: Contrast ratio is below WCAG AA (4.5:1).")
            sys.exit(1)
        else:
            print("SUCCESS: Contrast ratio meets WCAG AA.")
            sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
