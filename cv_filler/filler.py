"""
Vorlage Template Filler - fills the Lakomiec master template with new candidate data.
Uses XML manipulation on the unpacked docx for reliable results.
"""
import os
import io
import zipfile
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


TEMPLATE_PATH = Path(__file__).parent / "templates" / "Vorlage_Lebenslauf_MASTER.docx"

# Known placeholder values in the Lakomiec master template
PH = {
    "vorname":            "Lakokmiec",
    "nachname":           "Marcin Slawomir ",
    "nachname2":          "Marcin Slawomir",
    "geburtsdatum":       "15.03.1985",
    "geburtsort":         "Zdunska Wola, Polen",
    "starttermin":        "01.05.2026 ",
    "qual_1":             "- 2000-2004: Technisches Kolleg ZSE, Zdunska Wola, Polen",
    "qual_2":             "- 2011: S2-Zertifikat (Kran/Portal), UDT Lodz",
    "qual_3":             "- 2011: Schwei\u00dfzertifikat 135 MAG, IS Gliwice",
    "qual_4":             "- 2008: IPAF-Lizenz (Hubarbeitsbühnen)",
    "profil":             "Herr Lakokmiec ist ein hochqualifizierter Schwei\u00dfer und Teamleiter mit \u00fcber 15 Jahren Erfahrung in der Metallindustrie. Er verf\u00fcgt \u00fcber umfassende Expertise in den Verfahren 135, 136, 141 und 111 sowie in der F\u00fchrung gro\u00dfer Teams (bis zu 34 Mitarbeiter). Er hat weitreichende Erfahrung mit Kohlenstoffstahl, Edelstahl, Duplex und Hochdruckrohrleitungen.",
    # Work experience rows (date | employer | position | description)
    "j1_date":   "03.2024 \u2013 heute",
    "j1_emp":    "Temporary (Einsatz), Niederlande",
    "j1_pos":    "Supervisor Schwei\u00dfabteilung / Teamleiter / Schwei\u00dfer",
    "j1_desc":   "Leitung von 12 Schwei\u00dfern, ERP-Bedienung, Schwei\u00dfen von Stahlkonstruktionen (141, 135/136/138), Duplex, Super Duplex, SMO254.",
    "j2_date":   "08.2024 \u2013 03.2025",
    "j2_emp":    "Goldbeck Elementy Polska, Polen",
    "j2_pos":    "Supervisor Schwei\u00dfabteilung / Teamleiter",
    "j2_desc":   "F\u00fchrung von 34 Schwei\u00dfern, Qualit\u00e4tssicherung, Ausbildung von Mitarbeitern, ERP-Systeme.",
    "j3_date":   "11.2022 \u2013 07.2024",
    "j3_emp":    "Mamec Oy, Finnland",
    "j3_pos":    "Supervisor / Teamleiter / Schwei\u00dfer",
    "j3_desc":   "Leitung von 8 Schwei\u00dfern, Fertigung von Industriepumpen und Mixern (Schwarz- und Edelstahl), Verfahren 135/136/141/111.",
    "j4_date":   "01.2018 \u2013 06.2022",
    "j4_emp":    "Vahterus Oy, Finnland",
    "j4_pos":    "Schwei\u00dfer",
    "j4_desc":   "Schwei\u00dfen von Platten- und Rohrb\u00fcndelw\u00e4rmetauschern, Hochdruckrohrleitungen (WIG/141), Verfahren 135/136/141/111.",
    "j5_date":   "02.2013 \u2013 12.2017",
    "j5_emp":    "Bronto Skylift OY Ab, Finnland",
    "j5_pos":    "Schwei\u00dfer",
    "j5_desc":   "Schwei\u00dfen von LKW-Hubarbeitsbühnen und Hochdruckrohrleitungen (Edelstahl), Verfahren 135 MAG / 141 WIG.",
    "j6_date":   "11.2012 \u2013 02.2013",
    "j6_emp":    "Nakkilan Insin\u00f6\u00f6ritoimisto Oy, Finnland",
    "j6_pos":    "D\u00fcnnblechschwei\u00dfer / Monteur",
    "j6_desc":   "MAG-Schwei\u00dfen (135/136), Maschinenbedienung (S\u00e4ulenbohrmaschine, Abkantpresse).",
    "j7_date":   "04.2012 \u2013 10.2012",
    "j7_emp":    "Javasko OY, Finnland",
    "j7_pos":    "Schwei\u00dfer / Schlosser",
    "j7_desc":   "MAG-Schwei\u00dfen (135/136) f\u00fcr UT-Pr\u00fcfungen, Montage von Rahmen f\u00fcr Sandvik, Metso, ABB. Wandst\u00e4rken 3-120 mm.",
    # Education
    "edu_date":  "2000 \u2013 2004",
    "edu_inst":  "Technisches Kolleg ZSE, Zdunska Wola, Polen",
    "edu_desc":  "Schwerpunkt: Englisch und technische Grundlagen",
    # Weiterbildung
    "wb_date":   "2011",
    "wb_titel":  "Schwei\u00dfzertifikat 135 MAG, IS Gliwice",
    "wb_desc":   "S2-Zertifikat f\u00fcr Kran- und Portalbedienung",
    # Techniken
    "tech_1":    "MAG-Schwei\u00dfen (135/136): Expert",
    "tech_2":    "WIG-Schwei\u00dfen (141): Expert",
    "tech_3":    "E-Hand (111): Advanced",
    # Languages
    "lang_1":    "English:",
    "lang_1v":   "C1 (Exzellent)",
    "lang_2":    "Polnisch:",
    "lang_2v":   "Muttersprache",
    "lang_3":    "Deutsch: ",
    "lang_3v":   "Basic",
}


def _replace(content, old, new):
    """Safe replace — handles both exact and xml-space-preserve variants."""
    content = content.replace(f"<w:t>{old}</w:t>", f"<w:t>{new}</w:t>")
    content = content.replace(f'<w:t xml:space="preserve">{old}</w:t>',
                               f"<w:t>{new}</w:t>")
    return content


def _unpack_docx(docx_bytes):
    """Unpack docx bytes into a temp directory, return path."""
    tmp = tempfile.mkdtemp(prefix="vorlage_")
    with zipfile.ZipFile(io.BytesIO(docx_bytes)) as z:
        z.extractall(tmp)
    return tmp


def _pack_docx(tmp_dir):
    """Pack a directory back into docx bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                arc_path = os.path.relpath(abs_path, tmp_dir)
                zf.write(abs_path, arc_path)
    return buf.getvalue()


def _merge_runs(content):
    """Merge adjacent <w:t> runs with identical formatting (simplify XML)."""
    import re
    # Basic merge of adjacent text runs — good enough for our replacements
    return content


def fill_vorlage(data: dict) -> bytes:
    """
    Fill the Vorlage template with candidate data.
    Returns the filled docx as bytes.
    """
    # Load master template
    with open(TEMPLATE_PATH, "rb") as f:
        template_bytes = f.read()

    tmp_dir = _unpack_docx(template_bytes)

    try:
        doc_path = os.path.join(tmp_dir, "word", "document.xml")
        with open(doc_path, "r", encoding="utf-8") as f:
            xml = f.read()

        p = data.get("personal", {})
        jobs = data.get("berufserfahrung", [])
        edu = data.get("ausbildung", {})
        wb = data.get("weiterbildung", {})
        techs = data.get("techniken", [])
        langs = data.get("sprachen", [])
        quals = data.get("qualifikationen", ["", "", "", ""])
        while len(quals) < 4:
            quals.append("")

        # ── Personal data ──────────────────────────────────────────────────────
        xml = _replace(xml, PH["vorname"], p.get("vorname", ""))
        xml = _replace(xml, PH["nachname"], p.get("nachname", ""))
        xml = _replace(xml, PH["nachname2"], p.get("nachname", ""))
        xml = _replace(xml, PH["geburtsdatum"], p.get("geburtsdatum", ""))
        xml = _replace(xml, PH["geburtsort"], p.get("geburtsort", ""))
        xml = _replace(xml, PH["starttermin"], data.get("starttermin", "") + " ")

        # ── Qualifications bullets ──────────────────────────────────────────────
        xml = _replace(xml, PH["qual_1"], quals[0] if len(quals) > 0 else "")
        xml = _replace(xml, PH["qual_2"], quals[1] if len(quals) > 1 else "")
        xml = _replace(xml, PH["qual_3"], quals[2] if len(quals) > 2 else "")
        xml = _replace(xml, PH["qual_4"], quals[3] if len(quals) > 3 else "")

        # ── Profile summary ────────────────────────────────────────────────────
        xml = _replace(xml, PH["profil"], data.get("profil_zusammenfassung", ""))

        # ── Work experience (up to 7 rows in template) ─────────────────────────
        job_keys = ["j1", "j2", "j3", "j4", "j5", "j6", "j7"]
        for i, key in enumerate(job_keys):
            if i < len(jobs):
                job = jobs[i]
                xml = _replace(xml, PH[f"{key}_date"], job.get("zeitraum", ""))
                xml = _replace(xml, PH[f"{key}_emp"],  job.get("arbeitgeber", ""))
                xml = _replace(xml, PH[f"{key}_pos"],  job.get("position", ""))
                xml = _replace(xml, PH[f"{key}_desc"], job.get("taetigkeit", ""))
            else:
                # Clear unused rows
                xml = _replace(xml, PH[f"{key}_date"], "")
                xml = _replace(xml, PH[f"{key}_emp"],  "")
                xml = _replace(xml, PH[f"{key}_pos"],  "")
                xml = _replace(xml, PH[f"{key}_desc"], "")

        # ── Education ──────────────────────────────────────────────────────────
        xml = _replace(xml, PH["edu_date"], edu.get("zeitraum", ""))
        xml = _replace(xml, PH["edu_inst"], edu.get("einrichtung", ""))
        xml = _replace(xml, PH["edu_desc"], edu.get("beschreibung", ""))

        # ── Weiterbildung ──────────────────────────────────────────────────────
        xml = _replace(xml, PH["wb_date"],  wb.get("zeitraum", ""))
        xml = _replace(xml, PH["wb_titel"], wb.get("titel", ""))
        xml = _replace(xml, PH["wb_desc"],  wb.get("beschreibung", ""))

        # ── Techniken ──────────────────────────────────────────────────────────
        for i, key in enumerate(["tech_1", "tech_2", "tech_3"]):
            if i < len(techs):
                t = techs[i]
                xml = _replace(xml, PH[key], t.get("bezeichnung", ""))
            else:
                xml = _replace(xml, PH[key], "")

        # ── Languages ──────────────────────────────────────────────────────────
        lang_pairs = [("lang_1", "lang_1v"), ("lang_2", "lang_2v"), ("lang_3", "lang_3v")]
        for i, (lk, vk) in enumerate(lang_pairs):
            if i < len(langs):
                xml = _replace(xml, PH[lk], langs[i].get("sprache", "") + ":")
                # Remove the trailing colon if already present
                new_lbl = langs[i].get("sprache", "")
                if not new_lbl.endswith(":"):
                    new_lbl += ":"
                xml = xml.replace(f"<w:t>{langs[i].get('sprache','')}::</w:t>",
                                   f"<w:t>{new_lbl}</w:t>")
                xml = _replace(xml, PH[vk], langs[i].get("niveau", ""))
            else:
                xml = _replace(xml, PH[lk], "")
                xml = _replace(xml, PH[vk], "")

        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(xml)

        return _pack_docx(tmp_dir)

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def docx_to_pdf(docx_bytes: bytes) -> bytes:
    """Convert docx bytes to PDF bytes using LibreOffice or docx2pdf."""
    tmp_dir = tempfile.mkdtemp(prefix="pdf_conv_")
    try:
        docx_path = os.path.join(tmp_dir, "output.docx")
        pdf_path = os.path.join(tmp_dir, "output.pdf")

        with open(docx_path, "wb") as f:
            f.write(docx_bytes)

        # Try LibreOffice first
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if soffice:
            subprocess.run(
                [soffice, "--headless", "--convert-to", "pdf", docx_path, "--outdir", tmp_dir],
                capture_output=True, timeout=60
            )
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    return f.read()

        # Try docx2pdf (Windows with Word installed)
        try:
            from docx2pdf import convert
            convert(docx_path, pdf_path)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    return f.read()
        except Exception:
            pass

        return None
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
