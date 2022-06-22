import re

import panflute as pf

eq_label_numbers = dict()
quad_re = re.compile(r"\\qquad\{\((\d+)\)\}", re.MULTILINE)
eq_ref_re = re.compile(r"\[(eq:.+?)]")


def make_index(elm, _):
    if isinstance(elm, pf.Span) \
            and isinstance(elm.content[0], pf.Math) \
            and elm.content[0].format == "DisplayMath" \
            and elm.identifier.startswith("eq:") \
            and (m := quad_re.search(elm.content[0].text)) is not None:
        eq_label_numbers[elm.identifier] = m.group(1)


def update_eq_label(elm, _):
    if isinstance(elm, pf.Link) \
            and isinstance(elm.content[0], pf.Str) \
            and (m := eq_ref_re.search(elm.content[0].text)) is not None:
        labels = m.group(1).split(",")
        elm.content[0].text = " ,".join([eq_label_numbers[lb.strip()] for lb in labels])
        return elm


if __name__ == "__main__":
    pf.run_filters([make_index, update_eq_label])
