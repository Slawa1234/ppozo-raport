import streamlit as st
from io import BytesIO
import urllib.request
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

st.set_page_config(page_title="Generator Zbiorczego Raportu PPOŻ", layout="wide")

st.title("📸 Generator Zbiorczego Raportu PPOŻ")
st.subheader("Wersja stabilna: Pełne polskie znaki, podgląd zdjęć i dane techniczne")

# Funkcja pobierająca czcionkę z polskimi znakami, jeśli jeszcze nie istnieje
@st.cache_data
def load_fonts():
    try:
        # Pobieramy czcionkę DejaVuSans wspierającą polskie znaki
        urllib.request.urlretrieve("https://github.com/anthonyfok/fonts-ttf-dejavu/raw/master/DejaVuSans.ttf", "DejaVuSans.ttf")
        urllib.request.urlretrieve("https://github.com/anthonyfok/fonts-ttf-dejavu/raw/master/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf")
        urllib.request.urlretrieve("https://github.com/anthonyfok/fonts-ttf-dejavu/raw/master/DejaVuSans-Oblique.ttf", "DejaVuSans-Oblique.ttf")
        
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Oblique', 'DejaVuSans-Oblique.ttf'))
        return True
    except Exception as e:
        st.warning(f"Nie udało się pobrać czcionki DejaVuSans ({e}). Użyto czcionki domyślnej.")
        return False

has_custom_font = load_fonts()

# Inicjalizacja pamięci podręcznej dla dodanych systemów
if 'lista_systemow' not in st.session_state:
    st.session_state.lista_systemow = []

# Panel boczny - Dane projektu
st.sidebar.header("Dane Projektu")
project_name = st.sidebar.text_input("Nazwa Projektu", "MTU-München")
system_label = st.sidebar.text_input("Oznaczenie Ogólne", "047-01 / 047-02")
author = st.sidebar.text_input("Wykonawca (Visum)", "RH")

# Czyszczenie listy
if st.sidebar.button("🗑️ Wyczyść całą listę i zacznij od nowa"):
    st.session_state.lista_systemow = []
    st.toast("Lista systemów została wyczyszczona!")

st.write("### 1. Wgraj zdjęcia z budowy")
uploaded_files = st.file_uploader("Wgraj wszystkie zdjęcia dla tego projektu (.jpg, .png)", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files:
    mapa_plikow = {f.name: f for f in uploaded_files}
    opcje_zdjec = ["-- Wybierz zdjęcie --"] + list(mapa_plikow.keys())
    
    st.write("---")
    st.write("### 2. Skonfiguruj kolejny system (Przejście)")
    
    col_id, col_size, col_mat = st.columns([1, 1, 2])
    with col_id:
        id_systemu = st.text_input("ID Systemu (np. 387)", "")
    with col_size:
        rozmiar_systemu = st.text_input("Rozmiar (np. 150 x 150)", "")
    with col_mat:
        materialy_systemu = st.text_input("Użyte materiały (np. Hilti CFS / CP 611)", "")
    
    col_przed, col_po = st.columns(2)
    
    with col_przed:
        st.write("**STAN PRZED (Vor Zustand)**")
        wybrane_przed = st.selectbox("Wybierz zdjęcie dla Stanu Przed", opcje_zdjec, key="sb_przed")
        if wybrane_przed != "-- Wybierz zdjęcie --":
            st.image(mapa_plikow[wybrane_przed], caption=f"Podgląd: {wybrane_przed}", width=250)
            
    with col_po:
        st.write("**STAN PO (Nach Zustand)**")
        wybrane_po = st.selectbox("Wybierz zdjęcie dla Stanu Po", opcje_zdjec, key="sb_po")
        if wybrane_po != "-- Wybierz zdjęcie --":
            st.image(mapa_plikow[wybrane_po], caption=f"Podgląd: {wybrane_po}", width=250)

    if st.button("➕ Dodaj ten system do raportu zbiorczego"):
        if not id_systemu:
            st.error("Proszę wpisać ID Systemu!")
        elif wybrane_przed == "-- Wybierz zdjęcie --" or wybrane_po == "-- Wybierz zdjęcie --":
            st.error("Musisz wybrać oba zdjęcia (Przed i Po) dla tego systemu!")
        else:
            nowy_system = {
                "id": id_systemu,
                "rozmiar": rozmiar_systemu if rozmiar_systemu else "-",
                "materialy": materialy_systemu if materialy_systemu else "-",
                "foto_przed_nazwa": wybrane_przed,
                "foto_przed_bytes": mapa_plikow[wybrane_przed].getvalue(),
                "foto_po_nazwa": wybrane_po,
                "foto_po_bytes": mapa_plikow[wybrane_po].getvalue()
            }
            st.session_state.lista_systemow.append(nowy_system)
            st.success(f"Pomyślnie dodano System {id_systemu} do listy!")

    if st.session_state.lista_systemow:
        st.write("---")
        st.write(f"### 📋 Aktualna lista systemów w raporcie ({len(st.session_state.lista_systemow)})")
        
        for idx, sys in enumerate(st.session_state.lista_systemow):
            st.text(f"{idx+1}. System ID: {sys['id']} | Rozmiar: {sys['rozmiar']} | Materiały: {sys['materialy']}")
            
        st.write("---")
        st.write("### 3. Wygeneruj końcowy plik PDF")
        
        def generate_final_pdf(systemy):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            
            # Dobieramy czcionkę w zależności od powodzenia rejestracji DejaVuSans
            f_norm = 'DejaVuSans' if has_custom_font else 'Helvetica'
            f_bold = 'DejaVuSans-Bold' if has_custom_font else 'Helvetica-Bold'
            f_ital = 'DejaVuSans-Oblique' if has_custom_font else 'Helvetica-Oblique'
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName=f_bold, fontSize=22, textColor=colors.HexColor('#2c3e50'), spaceAfter=15)
            meta_style = ParagraphStyle('MetaStyle', parent=styles['Normal'], fontName=f_norm, fontSize=11, textColor=colors.HexColor('#34495e'), spaceAfter=5)
            h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontName=f_bold, fontSize=14, textColor=colors.HexColor('#2980b9'), spaceBefore=10, spaceAfter=10)
            italic_style = ParagraphStyle('ItalicStyle', parent=styles['Normal'], fontName=f_ital, fontSize=10, textColor=colors.HexColor('#2c3e50'))
            
            story.append(Paragraph("ZBIORCZY RAPORT FOTODOKUMENTACJI PPOŻ", title_style))
            story.append(Paragraph(f"<b>Projekt:</b> {project_name}", meta_style))
            story.append(Paragraph(f"<b>Oznaczenie Ogólne:</b> {system_label}", meta_style))
            story.append(Paragraph(f"<b>Wykonawca:</b> {author}", meta_style))
            story.append(Spacer(1, 20))
            
            for idx, sys in enumerate(systemy):
                if idx > 0:
                    story.append(PageBreak())
                    
                story.append(Paragraph(f"System ID: {sys['id']}", h2_style))
                story.append(Spacer(1, 10))
                
                try:
                    img_przed = Image(BytesIO(sys['foto_przed_bytes']), width=240, height=180)
                except:
                    img_przed = Paragraph("[Błąd zdjęcia Przed]", italic_style)
                    
                try:
                    img_po = Image(BytesIO(sys['foto_po_bytes']), width=240, height=180)
                except:
                    img_po = Paragraph("[Błąd zdjęcia Po]", italic_style)
                    
                table_data = [
                    [Paragraph("<b>STAN PRZED (Vor Zustand)</b>", meta_style), Paragraph("<b>STAN PO (Nach Zustand)</b>", meta_style)],
                    [img_przed, img_po],
                    [Paragraph(f"<b>Plik:</b> {sys['foto_przed_nazwa']}", italic_style), Paragraph(f"<b>Plik:</b> {sys['foto_po_nazwa']}", italic_style)],
                    [Paragraph(f"<b>Rozmiar / Abmessung:</b> {sys['rozmiar']}", meta_style), Paragraph(f"<b>Materiały / Materialien:</b> {sys['materialy']}", meta_style)],
                    [Paragraph("<b>PL:</b> Otwarty otwór instalacyjny przed uszczelnieniem.", italic_style), 
                     Paragraph("<b>PL:</b> Gotowe zabezpieczenie ppoż. Szczelina wypełniona materiałem ogniochronnym.", italic_style)],
                    [Paragraph("<b>DE:</b> Offene Installationsöffnung vor der Abschottung.", italic_style), 
                     Paragraph("<b>DE:</b> Fertige Brandschutzabdichtung. Der Spalt ist ordnungsgemäß versiegelt.", italic_style)]
                ]
                
                t = Table(table_data, colWidths=[260, 260])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (1,0), colors.HexColor('#f8f9fa')),
                    ('BACKGROUND', (0,3), (1,3), colors.HexColor('#f1f5f9')),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                    ('TOPPADDING', (0,0), (-1,-1), 8),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
                ]))
                story.append(t)
                
            doc.build(story)
            buffer.seek(0)
            return buffer

        if st.button("🚀 Utwórz zbiorczy plik PDF ze wszystkimi pozycjami"):
            with st.spinner("Generowanie raportu wielostronicowego z polskimi znakami..."):
                final_pdf = generate_final_pdf(st.session_state.lista_systemow)
                st.download_button(
                    label="📥 POBIERZ GOTOWY ZBIORCZY PDF",
                    data=final_pdf,
                    file_name=f"Raport_Zbiorczy_PPOZ_{project_name}.pdf",
                    mime="application/pdf"
                )
                st.success("Raport gotowy! Polskie znaki zostały naprawione.")
else:
    st.info("Wgraj zdjęcia, aby rozpocząć konfigurację raportu.")
