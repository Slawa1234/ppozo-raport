
import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Konfiguracja strony
st.set_page_config(page_title="Generator Fotodokumentacji PPOŻ", layout="wide")

st.title("Fotograficznej PPOŻ")
st.subheader("Automatyczne tworzenie raportów Przed / Po z pobieraniem PDF")

# Panel boczny - Dane projektu
st.sidebar.header("Dane Projektu")
project_name = st.sidebar.text_input("Nazwa Projektu", "MTU-München")
system_label = st.sidebar.text_input("Oznaczenie Systemu", "047-01 / 047-02")
author = st.sidebar.text_input("Wykonawca (Visum)", "RH")

st.write("### 1. Wgraj zdjęcia z budowy")
uploaded_files = st.file_uploader("Wybierz zdjęcia (.jpg, .png)", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files:
    # Zapisanie wgranych plików w pamięci podręcznej podręcznej (słownik nazwa: plik)
    file_dict = {f.name: f for f in uploaded_files}
    file_names = list(file_dict.keys())
    
    st.write("### 2. Skonfiguruj Przejście / System")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        system_id = st.text_input("ID Systemu (np. 387)", "387")
    with col2:
        before_img_name = st.selectbox("Zdjęcie: Stan Przed", ["Wybiersz plik..."] + file_names)
    with col3:
        after_img_name = st.selectbox("Zdjęcie: Stan Po", ["Wybierz plik..."] + file_names)
        
    st.write("---")
    
    # Przykładowe szablony opisów (możesz edytować w aplikacji)
    desc_pl_before = st.text_area("Opis PL - Stan Przed", "Otwarty otwór instalacyjny w przegrodzie suchej zabudowy.")
    desc_de_before = st.text_area("Opis DE - Vor Zustand", "Offene Installationsöffnung in der Trockenbauwand.")
    
    desc_pl_after = st.text_area("Opis PL - Stan Po", "Gotowe zabezpieczenie ppoż. Szczelina wypełniona wełną mineralną.")
    desc_de_after = st.text_area("Opis DE - Nach Zustand", "Fertige Brandschutzabdichtung. Der Spalt ist ausgefüllt.")

    # Funkcja generująca PDF ze zdjęciami
    def generate_pdf():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        styles = getSampleStyleSheet()
        
        # Style tekstu
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#2c3e50'), spaceAfter=15)
        meta_style = ParagraphStyle('MetaStyle', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#34495e'), spaceAfter=5)
        h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#2980b9'), spaceBefore=15, spaceAfter=10)
        bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')
        italic_style = ParagraphStyle('ItalicStyle', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Oblique', textColor=colors.HexColor('#2c3e50'))
        
        # Nagłówek dokumentu
        story.append(Paragraph("RAPORT FOTODOKUMENTACJI PPOŻ", title_style))
        story.append(Paragraph(f"<b>Projekt:</b> {project_name}", meta_style))
        story.append(Paragraph(f"<b>Oznaczenie Systemu:</b> {system_label}", meta_style))
        story.append(Paragraph(f"<b>Wykonawca:</b> {author}", meta_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph(f"System ID: {system_id}", h2_style))
        story.append(Spacer(1, 10))
        
        # Przygotowanie danych do tabeli (Zdjęcia i opisy)
        table_data = []
        
        # Wiersz 1: Nagłówki sekcji Przed / Po
        table_data.append([Paragraph("<b>STAN PRZED (Vor Zustand)</b>", meta_style), Paragraph("<b>STAN PO (Nach Zustand)</b>", meta_style)])
        
        # Wiersz 2: Zdjęcia
        img_before_flowable = Paragraph("[Brak zdjęcia]", italic_style)
        img_after_flowable = Paragraph("[Brak zdjęcia]", italic_style)
        
        # Bezpieczne wczytywanie i skalowanie zdjęć do PDF
        if before_img_name != "Wybierz plik...":
            try:
                img_before_data = BytesIO(file_dict[before_img_name].getvalue())
                img_before_flowable = Image(img_before_data, width=240, height=180)
            except:
                pass
                
        if after_img_name != "Wybierz plik...":
            try:
                img_after_data = BytesIO(file_dict[after_img_name].getvalue())
                img_after_flowable = Image(img_after_data, width=240, height=180)
            except:
                pass
                
        table_data.append([img_before_flowable, img_after_flowable])
        
        # Wiersz 3: Opisy PL
        table_data.append([
            Paragraph(f"<b>PL:</b> {desc_pl_before}", italic_style),
            Paragraph(f"<b>PL:</b> {desc_pl_after}", italic_style)
        ])
        
        # Wiersz 4: Opisy DE
        table_data.append([
            Paragraph(f"<b>DE:</b> {desc_de_before}", italic_style),
            Paragraph(f"<b>DE:</b> {desc_de_after}", italic_style)
        ])
        
        # Tworzenie i stylowanie tabeli dwukolumnowej
        t = Table(table_data, colWidths=[260, 260])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#f8f9fa')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ]))
        
        story.append(t)
        
        # Budowanie dokumentu
        doc.build(story)
        buffer.seek(0)
        return buffer

    # Przyciski akcji na dole strony
    st.write("### 3. Wygeneruj i pobierz raport")
    
    pdf_buffer = generate_pdf()
    
    st.download_button(
        label="📥 Pobierz raport jako PDF ze zdjęciami",
        data=pdf_buffer,
        file_name=f"Raport_PPOZ_System_{system_id}.pdf",
        mime="application/pdf"
    )
    st.success("Raport PDF został pomyślnie przygotowany! Kliknij przycisk powyżej, aby zapisać go na dysku.")
else:
    st.info("Proszę wgrać zdjęcia, aby odblokować opcje tworzenia raportu.")

