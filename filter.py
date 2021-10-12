import panflute as pf


def block(elm, _):
    if isinstance(elm, pf.Math):
        if elm.format == "DisplayMath" and elm.text.startswith(r"\begin{aligned}"):
            text = elm.text.replace(r"\begin{aligned}", "").replace(r"\end{aligned}", "").replace("\n", "")
            elms = list()
            for eq in text.split(r"\\"):
                elms.append(pf.Math(eq.replace("&", "")))
                elms.append(pf.SoftBreak())

            return elms[:-1]


if __name__ == "__main__":
    pf.run_filter(block)
