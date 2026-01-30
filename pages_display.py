from datetime import datetime
import pandas as pd
import streamlit as st

def showPage(file_path, page):
    #Params of different pages
    pages = {
        "Détails du compte Deezer": {"sheet": "1_creationData", "title": "📊 Détails du compte Deezer"},
        "Profil de l'utilisateur": {"sheet": "2_customizationData", "title": "🧍 Profil de l'utilisateur"},
        "Notifications": {"sheet": "3_setupData", "title": "🔔 Notifications"},
        "Options de paiement": {"sheet": "12_businessData", "title": "💸 Options de paiement"},
        "Misc": {"sheet": "13_navigationData", "title": "📂 Misc"},
    }

    sheet = pages[page]["sheet"]
    title = pages[page]["title"]

    liste_colonne_dates = ["Registration Date", "Date of birth", "Paid offer start date", "Paid offer end date", "Current payment period start date", "Current payment period end date", "Try and buy start date", "Try and buy end date", "Last login date", "Last content synchronization", "Last stream on mobile", "Last stream on web", "Last stream on flow", "Registration date"]

    with st.spinner("Chargement..."):
        df = pd.read_excel(file_path, sheet_name = sheet)
        #Print title of the page
        st.title(title)
        st.markdown("---")
        #Transform dataframe in dict
        data_dict = {col: df[col].iloc[0] if len(df) > 0 else "" for col in df.columns}
        for colonne, valeur in data_dict.items():
            #Formatting of values------------
            #Write 'N/A' if value is NaN
            if pd.isna(valeur):
                valeur = "N/A"
            #Format date values in 'dd/mm/yyyy' format
            if colonne in liste_colonne_dates:
                try:
                    date_obj = datetime.strptime(valeur, "%Y-%m-%d")
                    valeur = date_obj.strftime("%d/%m/%Y")
                except:
                    date_obj = valeur = "❓"
            #Format boolean values with emojis
            if str(valeur) == "True":
                valeur = "✅"
            if str(valeur) == "False":
                valeur = "❌"
            st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #bdc1be;">
                <span style="font-weight: 700; color: #A37BA2; font-size: 1.1em;">{colonne}</span>
                <span style="color: #222; font-size: 1.05em;">{valeur}</span>
            </div>
            """,
            unsafe_allow_html = True)
