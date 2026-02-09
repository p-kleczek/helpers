import re
from copy import copy
from typing import Pattern

out_lines = []
with open('input/wiki2tex.in') as fin:
    in_lines = fin.readlines()
    for line in in_lines:
        output = copy(line)

        output = re.sub(r"\t", ' & ', output)
        output = re.sub(r"(?<!\w)\.", r'\\None', output)
        output = re.sub(r"X", r'\\NonExist', output)
        output = re.sub(r"\n$", r' \\\\\n', output)

        out_lines.append(output)

if not out_lines[-1]:
    out_lines = out_lines[:-1]

with open('output/wiki2tex.out', 'w') as fout:
    fout.writelines(out_lines)

print("".join(out_lines))
