import streamlit as st
import os

# Konfiguracja strony
st.set_page_config(page_title="Generator Fotodokumentation PPOŻ", layout="wide")

st.title("🏗️ Generator Dokumentacji Fotograficznej PPOŻ")
st.subheader("Automatyczne tworzenie raportów Przed / Po dla MTU-München")

# Panel boczny - Dane projektu
st.sidebar.header("Dane Projektu")
projekt = st.sidebar.text_input("Nazwa Projektu", "MTU-München")
nr_systemu = st.sidebar.text_input("Oznaczenie Systemu", "047-01 / 047-02")
wykonawca = st.sidebar.text_input("Wykonawca (Visum)", "RH")

# Sekcja wgrywania plików
st.header("1. Wgraj zdjęcia z budowy")
uploaded_files = st.file_uploader("Wybierz zdjęcia (.jpg, .png)", accept_multiple_files=True, type=['jpg', 'png'])

# Przykładowa baza danych/szablonów opisów dla systemów
szablony_systemow = {
    "401": {"nazwa": "Główne przejście wieloprzewodowe", "opis_przed": "Otwarty przepust instalacyjny w konstrukcji suchej zabudowy przed aplikacją zabezpieczeń ppoż.", "opis_po": "Zamknięty i uszczelniony przepust instalacyjny. Zastosowano pełne uszczelnienie systemowe Hilti/Rockwool z naniesieniem ogniochronnej powłoki ablacyjnej."},
    "366": {"nazwa": "Przepust pionowy rury stalowej", "opis_przed": "Przygotowanie otworu rdzeniowego pod przepust pionowy rury stalowej. Wstępne dławienie wełną.", "opis_po": "Finalne uszczelnienie ppoż. Powierzchnia pokryta masą ablacyjną, zamontowana tabliczka znamionowa."},
    "387": {"nazwa": "Przepust rur ze stali nierdzewnej", "opis_przed": "Otwarty otwór instalacyjny w przegrodzie suchej zabudowy. Dwa rurociągi ze stali nierdzewnej bez uszczelnienia.", "opis_po": "Gotowe zabezpieczenie ppoż. Szczelina wypełniona wełną mineralną i zaciągnięta mastykiem ogniochronnym."}
}

if uploaded_files:
    st.header("2. Przypisz parametry i generuj opisy")
    
    # Tworzymy listę plików do łatwego wyboru
    file_names = [f.name for f in uploaded_files]
    
    # Formularz dla pojedynczego systemu (pętla lub pojedyncze dodawanie)
    sys_id = st.text_input("Podaj ID Systemu (np. 387, 401, 366):", "387")
    
    col1, col2 = st.columns(2)
    with col1:
        foto_przed = st.selectbox("Wybierz zdjęcie PRZED (Vor):", file_names)
    with col2:
        foto_po = st.selectbox("Wybierz zdjęcie PO (Nach):", file_names)
        
    # Pobieranie domyślnego szablonu jeśli istnieje
    dane_szablonu = szablony_systemow.get(sys_id, {"nazwa": "Nowy Przepust", "opis_przed": "", "opis_po": ""})
    
    nazwa_systemu = st.text_input("Nazwa elementu:", dane_szablonu["nazwa"])
    opis_przed = st.text_area("Opis techniczny (Vor Zustand):", dane_szablonu["opis_przed"])
    opis_po = st.text_area("Opis techniczny (Nach Zustand):", dane_szablonu["opis_po"])

    # Podgląd generowanego raportu w Markdown
    if st.button("Dodaj do raportu i wygeneruj tekst"):
        st.success("Dodano pomyślnie!")
        
        raport_md = f"""
## System {sys_id} ({nazwa_systemu})
**Lokalizacja:** {projekt} | **Oznaczenie:** {nr_systemu} | **ID:** {sys_id}

### Stan Przed (Vor Zustand)
* **Zdjęcie:** `{foto_przed}`
* **Opis:** {opis_przed}

### Stan Po (Nach Zustand)
* **Zdjęcie:** `{foto_po}`
* **Opis:** {opis_po} (Wykonawca: {wykonawca})
---
"""
        st.code(raport_md, language="markdown")

