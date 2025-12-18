import base64
import pandas as pd
import streamlit as st
import requests

st.markdown(
    """
    <style>
    button[kind="tertiary"]:hover {
        background-color: #FF0000 !important;
        color: white !important;
        border: 1px solid #FF0000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data(show_spinner = False)
def get_artist_info_from_id(artist_link):
    try:
        artist_id = artist_link.rstrip('/').split('/')[-1]
        url = f"https://api.deezer.com/artist/{artist_id}"
        response = requests.get(url)
        data = response.json()

        nb_fan = int(data.get("nb_fan", 0))

        return {
            "img_url": data.get("picture_medium", ""),
            "nb_album": int(data.get("nb_album", 0)),
            "nb_fan_formatted": f"{nb_fan:,}"
        }

    except Exception:
        return {
            "img_url": "",
            "nb_album": 0,
            "nb_fan_formatted": 0
        }

#Function needed to use placeholder in HTML
def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

#Popup appearing when clicking on the button containing infos about artist
@st.dialog("Détails de l'artiste")
def deezer_dialog(artist, link, artist_info):
    st.markdown(f"""
                # 🧑‍🎤 {artist}
                💿 <b>Sorties</b> : {artist_info['nb_album']}<br>
                🕺 <b>Fans</b> : {artist_info['nb_fan_formatted']}<br><br>""",
                unsafe_allow_html = True)
    st.markdown(
        f"""
        <a href="{link}" target="_blank"
           style="
               display:inline-block;
               padding:8px 14px;
               background:#A237FF;
               color:white;
               text-decoration:none;
               border-radius:6px;
               font-weight:600;
           ">
            Ouvrir sur Deezer
        </a>
        """,
        unsafe_allow_html = True
    )

def likedArtists(file_path):
    df = pd.read_excel(file_path, sheet_name = "4_favoriteArtist")
    st.title("🧑‍🎤 Artistes likés")
    st.markdown("---")

    artistsDict = {}
    for i in range(len(df)):
        artist = df.iloc[i]["Artist"]
        link = df.iloc[i]["Link"]
        artistsDict[artist] = link
   
    #Search bar
    search = st.text_input("🔎 Rechercher un artiste")
    if search:
        artistsDict = {k: v for k, v in artistsDict.items() if search.lower() in k.lower()}

    #Sort in alphabetical order
    artistsDict = dict(sorted(artistsDict.items(), key = lambda item: item[0].lower()))

    img_base64 = get_base64_image("placeholder_pics/placeholder-picture.jpg")
    placeholder = f"data:image/jpeg;base64,{img_base64}"

    #Print 4 by 4 artists with their picture
    artists = list(artistsDict.items())
    row_items = 4
    for i in range(0, len(artists), row_items):
        cols = st.columns(row_items)
        for j, (artist, link) in enumerate(artists[i:i+row_items]):
            with cols[j]:
                artist_info = get_artist_info_from_id(link)
                #Correct format of the link
                if not link.startswith("http"):
                    link = "https://" + link.lstrip("/")
                #If artist not found, use a placeholder image and do not display the link
                if artist_info == {'img_url': '', 'nb_album': 0, 'nb_fan_formatted': '0'}:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <img src="{placeholder}" alt="{artist}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{artist}</span>
                            </div>""",
                        unsafe_allow_html = True
                    )
                else:
                    st.markdown(
                        f"""
                        <div style="display:flex; flex-direction:column; align-items:center;">
                            <img src="{artist_info['img_url']}"
                                width="70"
                                style="border-radius:8px; box-shadow:0 2px 8px #0001; margin-bottom:8px">
                        </div>
                        """,
                        unsafe_allow_html = True
                    )
  
                    #Button with artist name
                    if st.button(
                        artist,
                        key = f"btn_{artist}_{i}_{j}",
                        use_container_width = True,
                        type = "tertiary"
                    ):
                        deezer_dialog(artist, link, artist_info)
