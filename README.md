# Resumix

Статический конструктор резюме на Astro. Форма оформлена как тетрадь: каждый шаг открывает новый «лист». Перед входом показывается уведомление о работе с персональными данными. Содержимое формы обрабатывается только в браузере; черновик сохраняется в `localStorage` лишь после явного включения настройки. Фото в черновик не записывается.

На последнем шаге приложение формирует ZIP с DOCX, Markdown, LaTeX и выбранным фото. Отдельный `generate_resume.py` позволяет создать LaTeX или PDF из JSON.

## Локальный запуск

```sh
npm ci
npm run dev
```

Для выпуска статического сайта:

```sh
npm run build
npm run preview
```

Готовый сайт находится в `dist/`. Для GitHub Pages используется workflow `.github/workflows/pages.yml`; в настройках репозитория выберите **GitHub Actions** как источник Pages. Для другого имени репозитория поменяйте `SITE_BASE` в workflow. Исходный `index.html` в корне оставлен как архив прежней версии и в Astro-сборку не входит.

## Генератор из JSON

```sh
python3 generate_resume.py resume_data.example.json -o output/resume.tex
python3 generate_resume.py resume_data.example.json -o output/resume.tex --pdf
python3 -m unittest -v
```

Для PDF требуется XeLaTeX или `latexmk` с XeLaTeX.
