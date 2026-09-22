import json
import tempfile
import unittest
from pathlib import Path

from generate_resume import build_document, tex


class ResumeGeneratorTests(unittest.TestCase):
    def test_latex_special_characters_are_escaped(self):
        self.assertEqual(tex("A&B_50%"), r"A\&B\_50\%")

    def test_example_generates_all_main_sections(self):
        data = json.loads(Path("resume_data.example.json").read_text(encoding="utf-8"))
        document = build_document(data, None)
        self.assertTrue(document.startswith("% !TeX program = xelatex"))
        self.assertIn(r"\usepackage{fontspec}", document)
        self.assertIn(r"\setmainfont{DejaVu Sans}", document)
        self.assertNotIn(r"\usepackage[T2A]{fontenc}", document)
        for section in ("О себе", "Опыт", "Проекты", "Профессиональные навыки", "Образование"):
            self.assertIn(rf"\section{{{section}}}", document)
        self.assertNotIn(r"\n\n", document)

    def test_photo_filename_is_not_latex_escaped(self):
        document = build_document({"name": "Имя Фамилия"}, "resume_photo.jpg")
        self.assertIn(r"\detokenize{resume_photo.jpg}", document)
        self.assertNotIn(r"resume\_photo.jpg", document)

    def test_empty_optional_sections_are_omitted(self):
        document = build_document({"name": "Имя Фамилия", "role": "Роль"}, None)
        self.assertNotIn(r"\section{Проекты}", document)
        self.assertNotIn(r"\section{Образование}", document)


if __name__ == "__main__":
    unittest.main()
