import re
from copy import copy
from typing import Pattern

person_re: Pattern = re.compile(r"\[\[(?P<person_id>people:start#\w+?)\|(?P<person_name>[^]]+?)]]", re.UNICODE)
bookmark_re: Pattern = re.compile(r"<BOOKMARK:(?P<bookmark_id>\w+?)>", re.UNICODE)
itemize_re: Pattern = re.compile(r"(?:^|(?<=%)) {2}\*")
encyplopedia_re: Pattern = re.compile(
    r"\[\[varia:(?:encyklopedia|slownik|swiadczenia_feudalne)#(?P<entry_id>\w+?)\|(?P<text>[^]]+?)]]", re.UNICODE)
place_re: Pattern = re.compile(r"\[\[(?P<place_id>places:start#\w+?)\|(?P<place_name>[^]]+?)]]", re.UNICODE)
measurement_unit_re: Pattern = re.compile(r"\[\[varia:miary#(?P<entry_id>\w+?)\|(?P<text>[^]]+?)]]", re.UNICODE)

jud_case_re: Pattern = re.compile(r"\[\[#(?P<case_id>sprawa_\w+?)\|(?P<desc>[^]]+?)]]", re.UNICODE)

latin_unknown_word_re: Pattern = re.compile(r"( #)|(# )", re.UNICODE)


def latin_unknown_word_repl(matchobj):
    return matchobj.group(0).replace("#", "*")


def jud_case_repl(matchobj):
    return f"\\courtref{{judcase:{matchobj.group('case_id')}}}{{{matchobj.group('desc')}}}"


bookmark_jud_case_re: Pattern = re.compile(r"<BOOKMARK:(?P<case_id>sprawa_\w+?)>", re.UNICODE)


def bookmark_jud_case_repl(matchobj):
    return f"\\label{{judcase:{matchobj.group('case_id')}}}"


# FIXME: footnote repl.

def person_repl(matchobj):
    return f"{matchobj.group('person_name')}\\MDWref{{{matchobj.group('person_id')}}}"


def bookmark_repl(matchobj):
    return f"\\label{{sec:{matchobj.group('bookmark_id')}}}"


def itemize_repl(matchobj):
    return f"\t\\item"


def encyplopedia_repl(matchobj):
    return f"\\href{{dct:{matchobj.group('entry_id')}}}{{{matchobj.group('text')}}}"


def place_repl(matchobj):
    return f"{matchobj.group('place_name')}\\MDWref{{{matchobj.group('place_id')}}}"


def measurement_unit_repl(matchobj):
    return f"\\href{{msr:{matchobj.group('entry_id')}}}{{{matchobj.group('text')}}}"


cite_re: Pattern = re.compile(r"\[\(:cite:(?:\w+:)*(?P<entry_id>\w+?)(>>page(s)?:(?P<pages>.+?))?\)]", re.UNICODE)


def cite_repl(matchobj):
    pages = f"[{matchobj.group('pages')}]" if 'pages' in matchobj.groupdict() and matchobj.group('pages') else ''
    return f"\\footcite{pages}{{{matchobj.group('entry_id')}}}"


acta_re: Pattern = re.compile(
    r"\b(?P<fond>TC|CC|TCz.|RCC|GS) (?P<sig>\w+), s\. \[\[sources:\w+#(?P<entry_id>\w+)\|(?P<page1>[\w\-—–]+)]](?:(—|–|--)(?P<page2>\w+))?",
    re.UNICODE)

fond_to_label_replacements = {
    'TC': 'tcrac',
    'TCz.': 'tczch',
    'CC': 'ccrac',
    'RCC': 'ccrac_rel',
    'GS': 'csand',
}


def acta_repl(matchobj):
    fond = matchobj.group('fond')
    sig = matchobj.group('sig')
    bib_entry_id = fond_to_label_replacements[fond]

    page1 = matchobj.group('page1')
    page2 = f"--{matchobj.group('page2')}" if ('page2' in matchobj.groupdict() and matchobj.group('page2')) else ""
    return f"\\cite[{page1}{page2}]{{{bib_entry_id}_{sig}}}\\MDWref{{{matchobj.group('entry_id')}}}"


footnote_re: Pattern = re.compile(r"\(\((?P<text>.+?)\)\)")


def footnote_repl(matchobj):
    return f"\\footnote{{{matchobj.group('text')}}}"


footcite_re: Pattern = re.compile(r"\\footnote\{\\cite(?P<content>(\[.+?])\{.+?})}")


def footcite_repl(matchobj):
    return f"\\footcite{matchobj.group('content')}"


out_lines = []
with open('input/wiki2tex.in') as fin:
    in_lines = fin.readlines()
    for line in in_lines:
        output = copy(line)

        output = re.sub(r" ", '~', output)  # Remove 'blank space'.
        output = re.sub(r"‎", '', output)  # Remove 'blank space'.
        output = re.sub(r"[–—]", '--', output)  # Remove 'blank space'.
        output = re.sub(r"\.{3}", r'\\textellipsis', output)  # Remove 'blank space'.

        output = bookmark_jud_case_re.sub(bookmark_jud_case_repl, output)
        output = jud_case_re.sub(jud_case_repl, output)

        output = person_re.sub(person_repl, output)
        output = bookmark_re.sub(bookmark_repl, output)
        output = itemize_re.sub(itemize_repl, output)
        output = encyplopedia_re.sub(encyplopedia_repl, output)
        output = place_re.sub(place_repl, output)
        output = measurement_unit_re.sub(measurement_unit_repl, output)
        output = cite_re.sub(cite_repl, output)
        output = acta_re.sub(acta_repl, output)
        output = footnote_re.sub(footnote_repl, output)
        output = footcite_re.sub(footcite_repl, output)
        output = latin_unknown_word_re.sub(latin_unknown_word_repl, output)

        out_lines.append(output)

with open('output/wiki2tex.out', 'w') as fout:
    fout.writelines(out_lines)

print("".join(out_lines))
