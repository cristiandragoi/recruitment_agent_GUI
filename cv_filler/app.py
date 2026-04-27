import dotenv
dotenv.load_dotenv()
"""
CV Vorlage Filler — AP Arbeitspartner
Upload any candidate CV → AI extracts data → fills the Vorlage template → download PDF + Word
"""
import streamlit as st
import json
import os
import sys
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CV Vorlage Filler · AP Arbeitspartner",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0; }
    .sub-title  { color: #666; margin-top: 0; margin-bottom: 2rem; }
    .step-box   { background: #f8f9fa; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; border-left: 4px solid #0066cc; }
    .success-box { background: #d4edda; border-radius: 8px; padding: 1rem; border-left: 4px solid #28a745; }
    .info-box   { background: #e8f4fd; border-radius: 8px; padding: 1rem; border-left: 4px solid #0066cc; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    .stDownloadButton>button { border-radius: 8px; font-weight: 600; background: #0066cc; color: white; }
    div[data-testid="stExpander"] { border-radius: 8px; border: 1px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/document.png", width=60)
    st.markdown("### ⚙️ Settings")

    # API Key
    api_key = st.text_input(
        "Anthropic API Key",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Your Anthropic API key for AI extraction"
    )

    st.divider()
    st.markdown("### 📋 Template")
    use_custom = st.checkbox("Use custom template", value=False)
    custom_template = None
    if use_custom:
        custom_template = st.file_uploader(
            "Upload Vorlage (.docx)",
            type=["docx"],
            help="Upload your own Vorlage template"
        )

    st.divider()
    st.markdown("""
    **How it works:**
    1. 📁 Upload the candidate's CV
    2. 🤖 AI extracts all data
    3. ✏️ Review & edit if needed
    4. ⬇️ Download filled Vorlage
    """)

    st.divider()
    st.caption("AP Arbeitspartner · CV Filler v1.0")


# ── Main content ───────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">📄 CV Vorlage Filler</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload a candidate CV → AI fills your Vorlage template automatically</p>',
            unsafe_allow_html=True)

# ── Step 1: Upload ─────────────────────────────────────────────────────────────
st.markdown("### Step 1 — Upload Candidate CV")
uploaded_file = st.file_uploader(
    "Drop the candidate's CV here (PDF or Word)",
    type=["pdf", "docx", "doc"],
    help="Any CV format works — PDF or Word"
)

if uploaded_file:
    st.markdown(f'<div class="success-box">✅ <b>{uploaded_file.name}</b> uploaded ({uploaded_file.size // 1024} KB)</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    # ── Step 2: Extract ────────────────────────────────────────────────────────
    st.markdown("### Step 2 — Extract & Review Data")

    if "extracted_data" not in st.session_state or \
       st.session_state.get("last_file") \!= uploaded_file.name:

        if st.button("🤖 Extract Data with AI", type="primary", use_container_width=True):
            if not api_key:
                st.error("Please enter your Anthropic API key in the sidebar.")
            else:
                with st.spinner("🔍 Reading CV and extracting data... (10-20 seconds)"):
                    try:
                        sys.path.insert(0, str(Path(__file__).parent))
                        from extractor import extract_cv_data
                        data = extract_cv_data(
                            uploaded_file.read(),
                            uploaded_file.name,
                            api_key
                        )
                        st.session_state["extracted_data"] = data
                        st.session_state["last_file"] = uploaded_file.name
                        st.success("✅ Data extracted successfully\!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")
    else:
        st.markdown('<div class="info-box">✅ Data already extracted. Edit below if needed, then generate.</div>',
                    unsafe_allow_html=True)
        if st.button("🔄 Re-extract from CV", use_container_width=True):
            del st.session_state["extracted_data"]
            st.rerun()

    # ── Edit extracted data ────────────────────────────────────────────────────
    if "extracted_data" in st.session_state:
        data = st.session_state["extracted_data"]

        col1, col2 = st.columns(2)

        with col1:
            with st.expander("👤 Personal Data", expanded=True):
                p = data.get("personal", {})
                p["anrede"] = st.selectbox("Anrede", ["Herr", "Frau"],
                                            index=0 if p.get("anrede") == "Herr" else 1)
                p["vorname"] = st.text_input("Vorname(n)", p.get("vorname", ""))
                p["nachname"] = st.text_input("Nachname", p.get("nachname", ""))
                p["geburtsdatum"] = st.text_input("Geburtsdatum", p.get("geburtsdatum", ""))
                p["geburtsort"] = st.text_input("Geburtsort", p.get("geburtsort", ""))
                p["staatsangehoerigkeit"] = st.text_input("Staatsangehörigkeit", p.get("staatsangehoerigkeit", ""))
                data["personal"] = p
                data["starttermin"] = st.text_input("Starttermin", data.get("starttermin", "01.05.2026"))

        with col2:
            with st.expander("📝 Profil & Qualifikationen", expanded=True):
                data["profil_zusammenfassung"] = st.text_area(
                    "Profil-Zusammenfassung",
                    data.get("profil_zusammenfassung", ""),
                    height=120
                )
                quals = data.get("qualifikationen", ["", "", "", ""])
                while len(quals) < 4:
                    quals.append("")
                st.markdown("**Qualifikationen (bullets):**")
                quals[0] = st.text_input("Qual. 1", quals[0])
                quals[1] = st.text_input("Qual. 2", quals[1])
                quals[2] = st.text_input("Qual. 3", quals[2])
                quals[3] = st.text_input("Qual. 4", quals[3])
                data["qualifikationen"] = quals

        with st.expander("💼 Berufserfahrung", expanded=True):
            jobs = data.get("berufserfahrung", [])
            updated_jobs = []
            for i, job in enumerate(jobs[:10]):
                st.markdown(f"**Job {i+1}**")
                c1, c2 = st.columns([1, 2])
                with c1:
                    job["zeitraum"] = st.text_input(f"Zeitraum #{i+1}", job.get("zeitraum", ""), key=f"jd{i}")
                with c2:
                    job["arbeitgeber"] = st.text_input(f"Arbeitgeber #{i+1}", job.get("arbeitgeber", ""), key=f"je{i}")
                c3, c4 = st.columns([1, 2])
                with c3:
                    job["position"] = st.text_input(f"Position #{i+1}", job.get("position", ""), key=f"jp{i}")
                with c4:
                    job["taetigkeit"] = st.text_input(f"Tätigkeit #{i+1}", job.get("taetigkeit", ""), key=f"jt{i}")
                updated_jobs.append(job)
                if i < len(jobs) - 1:
                    st.divider()
            data["berufserfahrung"] = updated_jobs

        col3, col4 = st.columns(2)
        with col3:
            with st.expander("🎓 Ausbildung & Weiterbildung"):
                edu = data.get("ausbildung", {})
                edu["zeitraum"] = st.text_input("Ausbildung Zeitraum", edu.get("zeitraum", ""))
                edu["einrichtung"] = st.text_input("Einrichtung", edu.get("einrichtung", ""))
                edu["beschreibung"] = st.text_input("Beschreibung", edu.get("beschreibung", ""))
                data["ausbildung"] = edu

                wb = data.get("weiterbildung", {})
                st.markdown("---")
                wb["zeitraum"] = st.text_input("Weiterbildung Jahr", wb.get("zeitraum", ""))
                wb["titel"] = st.text_input("Titel", wb.get("titel", ""))
                wb["beschreibung"] = st.text_input("Beschreibung ", wb.get("beschreibung", ""))
                data["weiterbildung"] = wb

        with col4:
            with st.expander("🔧 Techniken & Sprachen"):
                techs = data.get("techniken", [{}, {}, {}])
                while len(techs) < 3:
                    techs.append({})
                st.markdown("**Sonstige Techniken:**")
                for i in range(3):
                    t = techs[i]
                    tc1, tc2 = st.columns([3, 1])
                    with tc1:
                        t["bezeichnung"] = st.text_input(f"Technik {i+1}", t.get("bezeichnung", ""), key=f"tec{i}")
                    with tc2:
                        t["level"] = st.selectbox(f"Level {i+1}", ["Expert", "Advanced", "Intermediate", "Basic"],
                                                   index=["Expert","Advanced","Intermediate","Basic"].index(t.get("level","Advanced")) if t.get("level") in ["Expert","Advanced","Intermediate","Basic"] else 1,
                                                   key=f"tlv{i}")
                    techs[i] = t
                data["techniken"] = techs

                st.markdown("**Sprachkenntnisse:**")
                langs = data.get("sprachen", [{}, {}, {}])
                while len(langs) < 3:
                    langs.append({})
                for i in range(3):
                    lg = langs[i]
                    lc1, lc2 = st.columns(2)
                    with lc1:
                        lg["sprache"] = st.text_input(f"Sprache {i+1}", lg.get("sprache", ""), key=f"lng{i}")
                    with lc2:
                        lg["niveau"] = st.text_input(f"Niveau {i+1}", lg.get("niveau", ""), key=f"lnv{i}")
                    langs[i] = lg
                data["sprachen"] = langs

        st.session_state["extracted_data"] = data
        st.markdown("---")

        # ── Step 3: Generate ───────────────────────────────────────────────────
        st.markdown("### Step 3 — Generate Vorlage")

        col_gen1, col_gen2 = st.columns(2)
        with col_gen1:
            if st.button("⚡ Generate Word + PDF", type="primary", use_container_width=True):
                with st.spinner("🔨 Filling template..."):
                    try:
                        sys.path.insert(0, str(Path(__file__).parent))
                        from filler import fill_vorlage, docx_to_pdf

                        docx_bytes = fill_vorlage(st.session_state["extracted_data"])
                        pdf_bytes = docx_to_pdf(docx_bytes)

                        st.session_state["docx_bytes"] = docx_bytes
                        st.session_state["pdf_bytes"] = pdf_bytes

                        name = st.session_state["extracted_data"]["personal"].get("nachname", "Kandidat")
                        vorname = st.session_state["extracted_data"]["personal"].get("vorname", "")
                        st.session_state["candidate_name"] = f"{name}_{vorname}".replace(" ", "_")

                        st.success("✅ Vorlage generated\!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Generation failed: {e}")
                        st.exception(e)

        # ── Download buttons ───────────────────────────────────────────────────
        if "docx_bytes" in st.session_state:
            name = st.session_state.get("candidate_name", "Kandidat")
            st.markdown("#### ⬇️ Download")
            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button(
                    label="📄 Download Word (.docx)",
                    data=st.session_state["docx_bytes"],
                    file_name=f"Vorlage_Lebenslauf_{name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            with dl2:
                if st.session_state.get("pdf_bytes"):
                    st.download_button(
                        label="📕 Download PDF",
                        data=st.session_state["pdf_bytes"],
                        file_name=f"Vorlage_Lebenslauf_{name}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.info("PDF not available (LibreOffice/Word not found on server)")

else:
    # Landing state
    st.markdown("""
    <div class="step-box">
    <h4>👆 Upload a candidate CV to get started</h4>
    <p>Supported formats: <b>PDF</b>, <b>Word (.docx)</b></p>
    <p>The AI will automatically extract all candidate data and fill your Vorlage template.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🤖 AI Extraction\nAutomatically reads any CV format and extracts all fields")
    with c2:
        st.markdown("#### ✏️ Review & Edit\nCheck and correct any field before generating")
    with c3:
        st.markdown("#### ⬇️ Instant Download\nGet your filled Vorlage as Word + PDF")
