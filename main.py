import pandas as pd
import streamlit as st
from pages_display import afficher_page
from likedArtistsPage import likedArtists

#-------------------------Code starts here----------------------------
if __name__ == "__main__":
    #CSS styling
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background: #A237FF;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    file_path = "stats-deezer-updated.xlsx"
    pages = pd.read_excel(file_path, sheet_name=None)
    
    #Navigation menu
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Page à afficher",
        ("Détails du compte Deezer", "Profil de l'utilisateur", "Notifications", "Options de paiement", "Misc", "Artistes likés")
    )
    
    #Call to corresponding page function
    if page == "Artistes likés":
        likedArtists(file_path)
    else:
        afficher_page(file_path, page)