import re

import panflute as pf


def replace(elm, _):
    if hasattr(elm, "text"):
        updated = False
        for k, v in {
            r"\Im": r"\mathrm{Im}",
            r"\Re": r"\mathrm{Re}",
        }.items():
            if k in elm.text:
                elm.text = elm.text.replace(k, v)
                updated = True

        if updated:
            return elm


def aligned_block(elm, _):
    if isinstance(elm, pf.Math):
        if elm.format == "DisplayMath" and elm.text.startswith(r"\begin{aligned}"):
            text = elm.text.replace(r"\begin{aligned}", "").replace(r"\end{aligned}", "").replace("\n", "")
            elms = list()
            for eq in text.split(r"\\"):
                elms.append(pf.Math(eq.replace("&", "")))
                elms.append(pf.SoftBreak())

            return elms[:-1]


eq_label_re = re.compile(r"\\label{(eq:.+?)}", re.MULTILINE)


def extract_eq_label(elm, _):
    if isinstance(elm, pf.Math):
        if elm.format == "DisplayMath" and (m := eq_label_re.search(elm.text)):
            return [
                pf.Math(elm.text.replace(m.group(0), "")),
                pf.Space(),
                pf.Str(f"{{#{m.group(1)}}}")
            ]


if __name__ == "__main__":
    pf.run_filters([replace, aligned_block, extract_eq_label])
