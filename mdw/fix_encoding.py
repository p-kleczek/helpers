# Skrypt konwertujący znaki w pracach z serii "Inwentarz zabytków powiatu ... " S. Tomkowicza

import re

# ============================================================================


# text_org = """
# Leniak 1999 Leniak F., Miasto w latach 1565-1772, [w:] Limanowa. Dzieje miasta 1565-1945, pod red. F. Kiryka, t. 1, Kraków 1999, s. 69-209
# """.strip()

# ============================================================================

def fix_chars(raw_text: str) -> str:
    text_fixed = str(raw_text)

    replacement_tab = {
        '¿': 'ż',
        '³': 'ł',
        '¹': 'ą',
        '': 'ź',
        'ñ': 'ń',
        'ê': 'ę',
        '': 'ś',

        '\\oe ': 'ś',
        'a˛': 'ą',
        'e˛': 'ę',
        'a, ˛': 'ą,'
        
        '­ ': '',
    }

    for (co, cn) in replacement_tab.items():
        text_fixed = text_fixed.replace(co, cn)

    return text_fixed


# if __name__ == '__main__':
#     print()
#     print(fix_chars(text_org))

# ==================

if __name__ == '__main__':
    out_lines = []
    with open('input/wiki2tex.in') as fin:
        in_lines = fin.readlines()
        for line in in_lines:
            out_lines.append(fix_chars(line))

    if not out_lines[-1]:
        out_lines = out_lines[:-1]

    with open('output/wiki2tex.out', 'w') as fout:
        fout.writelines(out_lines)

    print("".join(out_lines))
