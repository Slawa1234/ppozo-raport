import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Generator Raportu PPOŻ", layout="wide")
st.title("📸 Generator Zbiorczego Raportu PPOŻ")

if 'lista_systemow' not in st.session_state:
    st.session_state.lista_systemow = []

# Panel boczny
st.sidebar.header("Dane Projektu")
project_name = st.sidebar.text_input("Nazwa Projektu", "MTU-München")
author = st.sidebar.text_input("Wykonawca (Visum)", "RH")

if st.sidebar.button("🗑️ Wyczyść listę"):
    st.session_state.lista_systemow = []

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
    if s_przed != "-- Wybierz --":
        c_przed.image(mapa_plikow[s_przed], width=200)
    s_po = c_po.selectbox("Stan Po", opcje)
    if s_po != "-- Wybierz --":
        c_po.image(mapa_plikow[s_po], width=200)
    
    if st.button("➕ Dodaj do listy"):
        if id_sys and s_przed != "-- Wybierz --" and s_po != "-- Wybierz --":
            st.session_state.lista_systemow.append({
                "id": id_sys, "rozmiar": rozmiar, "mat": materialy,
                "f_przed": mapa_plikow[s_przed].getvalue(), "f_po": mapa_plikow[s_po].getvalue()
            })
            st.success("Dodano!")

    if st.session_state.lista_systemow:
        if st.button("🚀 Generuj PDF"):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            
            # Styl z obsługą polskich znaków
            style = ParagraphStyle(
                'Normal',
                fontName='Helvetica',
                fontSize=10,
                leading=12,
                encoding='WinAnsiEncoding'
            )
            
            for sys in st.session_state.lista_systemow:
                story.append(Paragraph(f"System ID: {sys['id']}", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=14)))
                
                img1 = Image(BytesIO(sys['f_przed']), width=200, height=150)
                img2 = Image(BytesIO(sys['f_po']), width=200, height=150)
                
                # Tabela z pełnymi opisami
                data = [
                    [Paragraph("STAN PRZED", style), Paragraph("STAN PO", style)],
                    [img1, img2],
                    [Paragraph(f"Rozmiar: {sys['rozmiar']}", style), Paragraph(f"Materiały: {sys['mat']}", style)],
                    [Paragraph("PL: Otwarty otwór instalacyjny przed uszczelnieniem.", style), 
                     Paragraph("PL: Gotowe zabezpieczenie ppoż. Szczelina wypełniona materiałem ogniochronnym.", style)],
                    [Paragraph("DE: Offene Installationsöffnung vor der Abschottung.", style), 
                     Paragraph("DE: Fertige Brandschutzabdichtung. Der Spalt ist ordnungsgemäß versiegelt.", style)]
                ]
                
                t = Table(data, colWidths=[250, 250])
                t.setStyle(TableStyle([
                    ('BOX', (0,0), (-1,-1), 1, colors.black),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.black)
                ]))
                story.append(t)
                story.append(PageBreak())
            
            doc.build(story)
            buffer.seek(0)
            st.download_button("📥 POBIERZ PDF", buffer, "Raport.pdf", "application/pdf")


