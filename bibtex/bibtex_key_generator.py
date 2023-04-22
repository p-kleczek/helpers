import re

# ============================================================================

title_org = """
Księża wobec bezpieki na przykładzie Archidiecezji krakowskiej
znak
2007
""".strip()

title_org = """
Stanowisko Rady Stałej Konferencji Episkopatu Polski wobec działań Jana Pawła II odnoszących się do przestępstw seksualnych wobec małoletnich
episkopat
2022-11-18
""".strip()

# ============================================================================

def generate_bibtex_key(raw_key: str) -> str:
    title_new = raw_key.lower()

    title_new = re.sub(r'[ \-\n]', '_', title_new)

    replacement_tab = {
        'ą': 'a',
        'ć': 'c',
        'ę': 'e',
        'ł': 'l',
        'ń': 'n',
        'ó': 'o',
        'ś': 's',
        'ź': 'z',
        'ż': 'z',
    }

    for (co, cn) in replacement_tab.items():
        title_new = title_new.replace(co, cn)

    title_new = re.sub(r'\W', '', title_new)
    title_new = re.sub(r'_+', '_', title_new)

    return title_new


if __name__ == '__main__':
    print()
    print(generate_bibtex_key(title_org))
