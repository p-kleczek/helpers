import re
from copy import copy
from typing import Pattern

page_re: Pattern = re.compile(r"^s. (?P<page1>\d+)(-(?P<page2>\d+))?$", re.UNICODE)


def page_repl(matchobj):
    p1 = matchobj.group('page1')
    p2 = matchobj.group('page2')

    if p2:
        p1_i = int(p1)
        p2_i = int(p2)
        if p2_i < p1_i:
            p2 = p1[:-len(p2)] + p2


    p2_str = f"--{p2}" if p2 else ""

    return f"\\cite[{p1}{p2_str}]{{dzieje_wsi_niedzwiedzia_dobrowolski_1931}}"


out_lines = []
with open('input/wiki2tex.in') as fin:
    in_lines = fin.readlines()
    for line in in_lines:
        output = copy(line)

        output = re.sub(r" ", '~', output)  # Remove 'blank space'.
        output = re.sub(r"‎", '', output)  # Remove 'blank space'.
        output = re.sub(r"[–—]", '--', output)  # Remove 'blank space'.
        output = re.sub(r"\.{3}", r'\\textellipsis', output)  # Remove 'blank space'.

        output = page_re.sub(page_repl, output)

        out_lines.append(output)

with open('output/wiki2tex.out', 'w') as fout:
    fout.writelines(out_lines)

print("".join(out_lines))
