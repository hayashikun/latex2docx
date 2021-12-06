import re

import panflute as pf


def cannot_display(elm, _):
    if isinstance(elm, pf.Math):
        updated = False

        for k in [r"\begin{array}"]:
            if k in elm.text:
                elm.text = "[Equation(s) cannot be displayed.]"
                updated = True

        if updated:
            return elm


def _search(text, macro, num, br):
    idx = text.index(macro)
    macro_idx = idx
    idx += len(macro)
    starts = list()
    ends = list()
    for _ in range(num):
        while text[idx] == " ":
            idx += 1

        if text[idx] != br[0]:
            return None

        lv = 1
        starts.append(idx)
        while lv > 0:
            idx += 1
            if idx >= len(text):
                return None
            if text[idx] == br[1]:
                lv -= 1
            elif text[idx] == br[0]:
                lv += 1

        ends.append(idx)
        idx += 1

    return macro_idx, starts, ends


def replace(elm, _):
    if isinstance(elm, pf.Math):
        updated = False
        for k, v in {
            r"\Im": r"\mathrm{Im}",
            r"\Re": r"\mathrm{Re}",
            r"\vb": r"\mathbf",
            r"\notag": r"\nonumber",
            r"\varOmega": r"\mathit{\Omega}",
            r"\varGamma": r"\mathit{\Gamma}",
            r"\cross": r"\times",
            r"\vdot": r"\cdot",
            r"\qquad": r" ",
            r"[2ex]": r"",
            r"\left<": "<",
            r"\right>": ">",
        }.items():
            if k in elm.text:
                elm.text = elm.text.replace(k, v)
                updated = True

        macro_update = True
        while macro_update:
            macro_update = False
            for macro, num, br, s0, s1, s2 in [
                *[
                    (
                            f"\\{dv}{s}", n, "{}",
                            f"\\frac{s}" + "{d}" if n == 1 else "",
                            r"{" + ("d " if dv == "dv" else r"\partial "),
                            "}"
                    ) for n in [1, 2] for s in ["", "*"] for dv in ["dv", "pdv"]
                ],
                (r"\norm", 1, "{}", "", r"\left| \qty|", r"| \right|"),
                *[(r"\qty", 1, b, "", r"\left" + b[0], r"\right" + b[1]) for b in ["{}", "[]", "()", "||"]]
            ]:
                if macro in elm.text:
                    m = _search(elm.text, macro, num, br)
                    if m is not None:
                        idx = m[0]
                        t = elm.text[0:idx] + s0
                        idx += len(macro)
                        for s, e in zip(m[1], m[2]):
                            t += elm.text[idx:s] + s1 + elm.text[s + 1:e] + s2
                            idx = e + 1

                        t += elm.text[idx:]
                        elm.text = t
                        updated = True
                        macro_update = True

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
    pf.run_filters([cannot_display, replace, aligned_block, extract_eq_label])
