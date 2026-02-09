import os.path
import re

# ============================================================================

input_filename = "bibtex_key.in"

# ============================================================================

def generate_bibtex_key(raw_key: str) -> str:
    title_new = raw_key.lower()

    title_new = re.sub(r'[ ~\-\n]', '_', title_new)

    replacement_tab = {
        # interpunkcja
        '–': '_',
        # polski
        'ą': 'a',
        'ć': 'c',
        'ę': 'e',
        'ł': 'l',
        'ń': 'n',
        'ó': 'o',
        'ś': 's',
        'ź': 'z',
        'ż': 'z',
        # niemiecki
        'ß': 'ss',
        'ä': 'a',
        'ü': 'u',
        'ö': 'o',
        # czeski
        'á': 'a',
        'é': 'e',
        'ě': 'e',
        'ř': 'r',
        'č': 'c',
        'ů': 'u',
        'í': 'i',
        'ň': 'n',
        'š': 's',
        'ý': 'y',
        'ž': 'z',
    }

    for (co, cn) in replacement_tab.items():
        title_new = title_new.replace(co, cn)

    title_new = re.sub(r'\W', '', title_new)
    title_new = re.sub(r'_+', '_', title_new)

    return title_new


if __name__ == '__main__':
    if not os.path.isfile(input_filename):
        open(input_filename, 'w').close()

    title_org: str
    with open(input_filename, 'r') as f:
        title_org = '\n'.join(f.readlines()).strip()

    print()
    print(generate_bibtex_key(title_org))
