import streamlit as st
from pages_display import afficher_page
from likedArtistsPage import likedArtists
from likedAlbumsPage import likedAlbums
from likedPlaylistsPage import likedPlaylists

if __name__ == "__main__":
    st.sidebar.image("placeholder_pics/deezer-logo-coeur.jpg")
    st.sidebar.markdown(
    """
    <div style="
        position: sticky;
        top: 0;
        z-index: 10;
        padding: 5px 0;
    ">
        <h3 style="color:black; text-align:center; margin:0;">
            Unofficial Deezer stats app
        </h3>
    </div>
    """,
    unsafe_allow_html=True)

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

    file_path = "stats-deezer-updated-more.xlsx"

    #Navigation menu
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Page à afficher",
        ("Détails du compte Deezer", "Profil de l'utilisateur", "Notifications", "Options de paiement", "Misc", "Artistes likés", "Albums likés", "Playlists likées")
    )

    #Call to corresponding page function
    if page == "Artistes likés":
        likedArtists(file_path)
    elif page == "Albums likés":
        likedAlbums(file_path)
    elif page == "Playlists likées":
        likedPlaylists(file_path)
    else:
        afficher_page(file_path, page)
