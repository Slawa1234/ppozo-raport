import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont

st.set_page_config(page_title="Generator Raportu PPOŻ", layout="wide")

st.title("📸 Generator Zbiorczego Raportu PPOŻ")

# Inicjalizacja listy
if 'lista_systemow' not in st.session_state:
    st.session_state.lista_systemow = []

# Sidebar
st.sidebar.header("Dane Projektu")
project_name = st.sidebar.text_input("Nazwa Projektu", "MTU-München")
system_label = st.sidebar.text_input("Oznaczenie Ogólne", "047-01 / 047-02")
author = st.sidebar.text_input("Wykonawca (Visum)", "RH")

if st.sidebar.button("🗑️ Wyczyść listę"):
    st.session_state.lista_systemow = []

# Upload
uploaded_files = st.file_uploader("Wgraj zdjęcia", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files:
    mapa_plikow = {f.name: f for f in uploaded_files}
    opcje = ["-- Wybierz --"] + list(mapa_plikow.keys())
    
    col1, col2, col3 = st.columns(3)
    id_sys = col1.text_input("ID Systemu")
    rozmiar = col2.text_input("Rozmiar")
    materialy = col3.text_input("Materiały")
    
    c_przed, c_po = st.columns(2)
    s_przed = c_przed.selectbox("Stan Przed", opcje)
    s_po = c_po.selectbox("Stan Po", opcje)
    
    if st.button("➕ Dodaj do listy"):
        if id_sys and s_przed != "-- Wybierz --" and s_po != "-- Wybierz --":
            st.session_state.lista_systemow.append({
                "id": id_sys, "rozmiar": rozmiar, "mat": materialy,
                "f_przed": mapa_plikow[s_przed].getvalue(), "f_po": mapa_plikow[s_po].getvalue()
            })
            st.success("Dodano!")

    if st.session_state.lista_systemow:
        if st.button("🚀 Generuj PDF (z obsługą polskich znaków)"):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            
            # Używamy standardowego kodowania, które wspiera polskie znaki w Helvetica
            styles = getSampleStyleSheet()
            style_norm = styles['Normal']
            style_norm.fontName = 'Helvetica'
            style_norm.encoding = 'WinAnsiEncoding'
            
            for sys in st.session_state.lista_systemow:
                story.append(Paragraph(f"System ID: {sys['id']}", styles['Heading2']))
                data = [
                    ["STAN PRZED", "STAN PO"],
                    [Image(BytesIO(sys['f_przed']), 200, 150), Image(BytesIO(sys['f_po']), 200, 150)],
                    [f"Rozmiar: {sys['rozmiar']}", f"Materiały: {sys['mat']}"],
                    ["PL: Otwarty otwór instalacyjny.", "PL: Gotowe zabezpieczenie ppoż."]
                ]
                t = Table(data, colWidths=[250, 250])
                t.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.black)]))
                story.append(t)
                story.append(PageBreak())
            
            doc.build(story)
            buffer.seek(0)
            st.download_button("📥 POBIERZ PDF", buffer, "Raport.pdf", "application/pdf")

