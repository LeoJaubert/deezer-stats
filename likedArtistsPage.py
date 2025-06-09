import pandas as pd
import streamlit as st
import requests
import base64

@st.cache_data(show_spinner=False)
def get_artist_picture_from_id(artist_link):
    # Extrait l'ID de l'artiste depuis le lien
    try:
        artist_id = artist_link.rstrip('/').split('/')[-1]
        url = f"https://api.deezer.com/artist/{artist_id}"
        response = requests.get(url)
        data = response.json()
        if "picture_medium" in data:
            return data["picture_medium"]
    except Exception:
        pass
    return None

#Function needed to use placeholder in HTML
def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def likedArtists(file_path):
    df = pd.read_excel(file_path, sheet_name="4_favoriteArtist")
    st.title("🧑‍🎤 Artistes likés")
    st.markdown("---")

    artistsDict = {}
    for i in range(len(df)):
        artist = df.iloc[i]["Artist"]
        link = df.iloc[i]["Link"]
        artistsDict[artist] = link

    #Sort in alphabetical order
    artistsDict = dict(sorted(artistsDict.items(), key=lambda item: item[0].lower()))
    
    img_base64 = get_base64_image("placeholder_pics/placeholder-picture.jpg")
    placeholder = f"data:image/jpeg;base64,{img_base64}"

    #Print 4 by 4 artists with their picture and link to their Deezer page
    artists = list(artistsDict.items())
    row_items = 4
    for i in range(0, len(artists), row_items):
        cols = st.columns(row_items)
        for j, (artist, link) in enumerate(artists[i:i+row_items]):
            with cols[j]:
                img_url = get_artist_picture_from_id(link)
                #Correct format of the link
                if not link.startswith("http"):
                    link = "https://" + link.lstrip("/")
                #If artist not found, use a placeholder image and do not display the link
                if img_url is None:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <img src="{placeholder}" alt="{artist}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{artist}</span>
                            </div>""",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <a href="{link}" target="_blank" style="text-decoration: none;">
                                    <img src="{img_url}" alt="{artist}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                </a>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{artist}</span>
                            </div>""",
                        unsafe_allow_html=True
                    )