# Konwersja pliku .bib na listę {tytuł -> bib_label} pod kątem tabeli z wykazem stanu opracowania pozycji bibliograficznych.
import re
from copy import copy, deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Pattern, List, Dict

bib_dir: Path = Path("/home/pawel/Projects/MszanaDln/mszana_dolna_text/bib/")
bib_file_path: Path = bib_dir / "main.bib"

label_re: Pattern = re.compile(r'^@(?P<etype>\w+)\{(?P<label>\w+),')
data_re: Pattern = re.compile(r'^\s+(?P<field>\w+)\s+= \{(?P<data>.*)},$')
end_of_entry_re: Pattern = re.compile(r'^}$')


@dataclass
class Entry:
    label: str = ""
    etype: str = ""
    data: Dict[str, str] = field(default_factory=dict)


raw_entries: Dict[str, Entry] = {}

with open(bib_file_path) as f:
    lines = f.readlines()

    entry = Entry()
    for line in lines:
        line = line.rstrip()
        if m := label_re.fullmatch(line):
            entry.label = m.group('label')
            entry.etype = m.group('etype')
        if m := data_re.fullmatch(line):
            entry.data[m.group('field')] = m.group('data')

        if end_of_entry_re.fullmatch(line):
            raw_entries[entry.label] = copy(entry)
            entry = Entry()

mod_entries: List[Entry] = []

for entry in raw_entries.values():
    this_data = copy(entry.data)
    while cref_label := this_data.get('crossref'):
        if cref_label == 'CROSSREF':
            break
        new_data = copy(raw_entries[cref_label].data)
        del this_data['crossref']
        new_data.update(this_data)
        this_data = new_data

    new_entry = deepcopy(entry)
    new_entry.data = this_data
    mod_entries.append(new_entry)

for entry in mod_entries:
    title = ""
    if mt := entry.data.get('maintitle'):
        title += f"{mt} "
    if bt := entry.data.get('booktitle'):
        title += f"{bt} "
    if (vol := entry.data.get('volume')) and entry.etype != 'Article':
        if vol not in ['VOL', 'VOLUME']:
            title += f"[T.{vol}] "
    if title:
        title += " : "
    if tit := entry.data.get('title'):
        title += f"{tit} "
    if p := entry.data.get('part'):
        title += f" [Cz. {p}] "
    elif p := entry.data.get('partpl'):
        title += f" [Cz. {p}] "

    authors = ""
    if aut := entry.data.get('author'):
        authors += aut
    elif ed := entry.data.get('editor'):
        authors += ed
    elif eda := entry.data.get('editora'):
        authors += eda

    authors_mod = ""
    if authors and authors not in ['AUTHOR', 'EDITOR', 'EDITORA']:
        authors_lst = authors.split(" and ")
        authors_lst_short = []
        for author in authors_lst:
            chunks = author.split(' ')
            try:
                authors_lst_short.append(f"{chunks[0][0]}. {chunks[-1]}")
            except IndexError as e:
                pass
        authors_mod = "; ".join(authors_lst_short)

    date = ""
    if d := entry.data.get('date'):
        date += d
    elif y := entry.data.get('year'):
        date += y

    url = ""
    if u := entry.data.get('url'):
        if u != "URL":
            url += u

    s = " ; ".join([e.strip() for e in [title, authors, date]])

    if title.startswith('['):
        print(f"{entry.label} : {s}")

    s_ods = "\t".join([e.strip() for e in [title, "", entry.label, authors_mod, date, url]])
    print(s_ods)

# print(mod_entries)