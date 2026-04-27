"""
CV Data Extractor — uses Claude AI to extract structured data from any CV format.
"""
import json
import re
import anthropic


EXTRACTION_PROMPT = """You are an expert CV data extractor for a German staffing agency.
Extract ALL information from the following CV text and return it as a JSON object.

Rules:
- Dates in German format: "MM.YYYY - MM.YYYY" or "YYYY - YYYY"
- If a field is missing, use empty string ""
- Work experience sorted newest first, up to 10 entries
- Keep descriptions concise (1-2 sentences per job)
- Staatsangehoerigkeit always in German (e.g. "Polnisch", "Deutsch")
- Language levels: Muttersprache, C2, C1, B2, B1, Grundkenntnisse, Gute Kenntnisse, Verhandlungssicher
- Skill levels: Expert, Advanced, Intermediate, Basic
- Anrede: "Herr" or "Frau"

Return ONLY valid JSON, no markdown, no explanation:

{
  "personal": {
    "anrede": "Herr",
    "vorname": "First name(s)",
    "nachname": "Last name",
    "geburtsdatum": "DD.MM.YYYY",
    "geburtsort": "City, Country",
    "staatsangehoerigkeit": "Polnisch"
  },
  "starttermin": "01.05.2026",
  "qualifikationen": [
    "- Qualification 1",
    "- Qualification 2",
    "- Qualification 3"
  ],
  "profil_zusammenfassung": "2-3 sentence summary in German starting with Herr/Frau [Nachname] ist...",
  "berufserfahrung": [
    {
      "zeitraum": "MM.YYYY - MM.YYYY",
      "arbeitgeber": "Company, Country",
      "position": "Job title",
      "taetigkeit": "Main tasks description."
    }
  ],
  "ausbildung": {
    "zeitraum": "YYYY - YYYY",
    "einrichtung": "School / Institution, Country",
    "beschreibung": "Degree or qualification"
  },
  "weiterbildung": {
    "zeitraum": "YYYY",
    "titel": "Training course name",
    "beschreibung": "Brief description"
  },
  "techniken": [
    {"bezeichnung": "Skill 1: Expert", "level": "Expert"},
    {"bezeichnung": "Skill 2: Advanced", "level": "Advanced"},
    {"bezeichnung": "Skill 3: Advanced", "level": "Advanced"}
  ],
  "sprachen": [
    {"sprache": "Language 1:", "niveau": "Level 1"},
    {"sprache": "Language 2:", "niveau": "Level 2"},
    {"sprache": "Language 3:", "niveau": "Level 3"}
  ]
}

CV TEXT:
"""


def read_docx_text(file_bytes):
    import zipfile, io
    from xml.etree import ElementTree as ET
    texts = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)
            for elem in tree.getroot().iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if elem.text:
                    texts.append(elem.text)
    return " ".join(texts)


def read_pdf_text(file_bytes):
    try:
        import pypdf, io
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception:
        return ""


def extract_cv_data(file_bytes, filename, api_key):
    ext = filename.lower().rsplit(".", 1)[-1]
    cv_text = read_pdf_text(file_bytes) if ext == "pdf" else read_docx_text(file_bytes)
    if not cv_text.strip():
        raise ValueError("Could not extract text from file.")

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": EXTRACTION_PROMPT + cv_text[:12000]}]
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"^```json\s*|^```\s*|\s*```$", "", raw, flags=re.MULTILINE)
    return json.loads(raw)
