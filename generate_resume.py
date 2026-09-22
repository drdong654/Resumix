#!/usr/bin/env python3
"""Generate a compact A4 LaTeX resume from JSON data."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from string import Template
from typing import Any


LATEX_SPECIAL = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def tex(value: Any) -> str:
    """Escape user-provided plain text for LaTeX."""
    return "".join(LATEX_SPECIAL.get(char, char) for char in str(value or "").strip())


def url(value: Any) -> str:
    """Escape a URL used as a hyperref target."""
    return str(value or "").strip().replace("%", r"\%").replace("#", r"\#")


def items(values: list[Any], label: str = "") -> str:
    rows = []
    for value in values or []:
        if str(value).strip():
            rows.append(f"\\resumeItem{{{tex(label)}}}{{{tex(value)}}}")
    if not rows:
        return ""
    return "\\resumeItemListStart\n\n" + "\n\n".join(rows) + "\n\n\\resumeItemListEnd"


def subheading(
    left_top: Any,
    right_top: Any,
    left_bottom: Any,
    right_bottom: Any,
    *,
    large: bool = False,
    bold_right: bool = True,
) -> str:
    left = tex(left_top)
    if large:
        left = rf"\Large {left}"
    right = tex(right_top)
    if bold_right:
        right = rf"\textbf{{{right}}}"
    return (
        "\\resumeSubheading\n"
        f"  {{{left}}}\n"
        f"  {{{right}}}\n"
        f"  {{{tex(left_bottom)}}}\n"
        f"  {{{tex(right_bottom)}}}"
    )


def section(title: str, body: str) -> str:
    return f"\\section{{{tex(title)}}}\n\n{body.strip()}" if body.strip() else ""


def render_header(data: dict[str, Any], photo_name: str | None) -> str:
    github = data.get("github", "")
    messenger = data.get("messenger", "")
    email = data.get("email", "")
    phone = data.get("phone", "")

    links = []
    if github:
        links.append(rf"\href{{{url(github)}}}{{{tex(github.removeprefix('https://').removeprefix('http://'))}}}")
    if messenger:
        messenger_url = data.get("messenger_url", "")
        links.append(rf"\href{{{url(messenger_url)}}}{{{tex(messenger)}}}" if messenger_url else tex(messenger))

    info_lines = [
        rf"{{\Large \textbf{{{tex(data.get('name', 'Имя Фамилия'))}}}}}\hfill {rf'\href{{mailto:{url(email)}}}{{{tex(email)}}}' if email else ''}",
        rf"{{\textbf{{{tex(data.get('role', 'Целевая должность'))}}}}}\hfill {tex(phone)}",
    ]
    if links or data.get("location"):
        info_lines.append(f"{' \\quad '.join(links)}\\hfill {tex(data.get('location', ''))}")
    info = "\\\\[4pt]\n\n    ".join(info_lines)

    if not photo_name:
        return rf"\noindent\parbox[t]{{\linewidth}}{{\vspace{{3pt}}{info}}}"

    return rf"""\noindent
\parbox[t]{{2.5cm}}{{
    \vspace{{0pt}}
    \includegraphics[width=2.3cm]{{\detokenize{{{photo_name}}}}}
}}
\hfill
\parbox[t]{{\dimexpr\linewidth-3cm\relax}}{{
    \vspace{{3pt}}

    {info}
}}"""


def render_experience(records: list[dict[str, Any]]) -> str:
    blocks = []
    for record in records or []:
        if not record.get("company") and not record.get("position"):
            continue
        block = [
            subheading(record.get("company"), record.get("position"), record.get("area"), record.get("period"), large=True),
        ]
        if record.get("stack"):
            block.append(f"\\vspace{{7pt}}\n\n\\textbf{{Инструменты:}} {tex(record['stack'])}")
        responsibilities = items(record.get("responsibilities", []))
        if responsibilities:
            block.append(r"\vspace{3pt}" + "\n\n" + responsibilities)
        results = items(record.get("results", []))
        if results:
            block.append(r"\vspace{3pt}" + "\n\n\\textbf{Результаты:}\n\n" + results)
        blocks.append("\n\n".join(block))
    if not blocks:
        return ""
    return "\\resumeSubHeadingListStart\n\n" + "\n\n\\vspace{7pt}\n\n".join(blocks) + "\n\n\\resumeSubHeadingListEnd"


def render_projects(records: list[dict[str, Any]]) -> str:
    blocks = []
    for record in records or []:
        if not record.get("name"):
            continue
        block = [
            subheading(record.get("name"), record.get("role"), record.get("description"), record.get("type"), large=True),
        ]
        if record.get("stack"):
            block.append(f"\\vspace{{5pt}}\n\n\\textbf{{Методы и инструменты:}} {tex(record['stack'])}")
        details = items(record.get("details", []))
        if details:
            block.append(r"\vspace{2pt}" + "\n\n" + details)
        blocks.append("\n\n".join(block))
    if not blocks:
        return ""
    return "\\resumeSubHeadingListStart\n\n" + "\n\n\\vspace{7pt}\n\n".join(blocks) + "\n\n\\resumeSubHeadingListEnd"


def render_skills(skills: list[dict[str, Any]]) -> str:
    rows = []
    for skill in skills or []:
        if skill.get("items"):
            rows.append(rf"\resumeItem{{{tex(skill.get('category'))}}}{{{tex(skill.get('items'))}}}")
    return "\\resumeItemListStart\n\n" + "\n\n".join(rows) + "\n\n\\resumeItemListEnd" if rows else ""


def render_education(records: list[dict[str, Any]]) -> str:
    rows = []
    for record in records or []:
        if record.get("program") or record.get("institution"):
            rows.append(
                subheading(
                    record.get("program"),
                    record.get("institution"),
                    record.get("degree"),
                    record.get("years"),
                    bold_right=False,
                )
            )
    return "\\resumeSubHeadingListStart\n\n" + "\n\n\\vspace{2pt}\n\n".join(rows) + "\n\n\\resumeSubHeadingListEnd" if rows else ""


DOCUMENT = Template(r"""% !TeX program = xelatex
\documentclass[a4paper,11pt]{article}
\usepackage{fontspec}
\usepackage{polyglossia}
\setdefaultlanguage{russian}
\setotherlanguage{english}
\setmainfont{DejaVu Sans}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage[usenames,dvipsnames]{color}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{tabularx}
\usepackage{graphicx}
\usepackage[hidelinks]{hyperref}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\addtolength{\oddsidemargin}{-0.375in}
\addtolength{\evensidemargin}{-0.375in}
\addtolength{\textwidth}{0.75in}
\addtolength{\topmargin}{-0.55in}
\addtolength{\textheight}{1.1in}
\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\newcommand{\resumeItem}[2]{
  \item\small{\if\relax\detokenize{#1}\relax #2\else\textbf{#1}: #2\fi\vspace{-2pt}}
}
\newcommand{\resumeSubheading}[4]{
  \vspace{-1pt}\item
  \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
    \textbf{#1} & #2 \\
    \textit{\small #3} & \textit{\small #4} \\
  \end{tabular*}\vspace{-5pt}
}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0pt,label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=18pt]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

${header}

\vspace{4pt}

${about}

${experience}

${projects}

${skills}

${education}

${courses}

${languages}

\end{document}
""")


def build_document(data: dict[str, Any], photo_name: str | None) -> str:
    about = section("О себе", rf"\small{{{tex(data.get('about', ''))}}}") if data.get("about") else ""
    courses = render_skills(data.get("additional_education", []))
    languages = tex(data.get("languages", ""))
    return DOCUMENT.substitute(
        header=render_header(data, photo_name),
        about=about,
        experience=section("Опыт", render_experience(data.get("experience", []))),
        projects=section("Проекты", render_projects(data.get("projects", []))),
        skills=section("Профессиональные навыки", render_skills(data.get("skills", []))),
        education=section("Образование", render_education(data.get("education", []))),
        courses=section("Дополнительное обучение", courses),
        languages=f"\\vspace{{2pt}}\n\n\\textbf{{Языки:}} {languages}" if languages else "",
    )


def compile_pdf(tex_path: Path) -> None:
    command = shutil.which("latexmk")
    if command:
        args = [command, "-xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
        runs = 1
    else:
        command = shutil.which("xelatex")
        if not command:
            raise RuntimeError("Для --pdf установите XeLaTeX или latexmk с XeLaTeX.")
        args = [command, "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
        runs = 2
    for _ in range(runs):
        subprocess.run(args, cwd=tex_path.parent, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Создать LaTeX-резюме из JSON")
    parser.add_argument("data", type=Path, help="JSON-файл с данными резюме")
    parser.add_argument("-o", "--output", type=Path, default=Path("resume.tex"), help="Выходной .tex файл")
    parser.add_argument("--pdf", action="store_true", help="Также собрать PDF через latexmk или pdflatex")
    args = parser.parse_args()

    try:
        data = json.loads(args.data.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("корневое значение JSON должно быть объектом")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        photo_name = None
        if data.get("photo"):
            photo_path = (args.data.parent / data["photo"]).resolve()
            if not photo_path.is_file():
                raise FileNotFoundError(f"фото не найдено: {photo_path}")
            photo_name = "resume_photo" + photo_path.suffix.lower()
            shutil.copy2(photo_path, args.output.parent / photo_name)
        args.output.write_text(build_document(data, photo_name), encoding="utf-8")
        if args.pdf:
            compile_pdf(args.output)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError, RuntimeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    print(f"Создано: {args.output}")
    if args.pdf:
        print(f"Создано: {args.output.with_suffix('.pdf')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
