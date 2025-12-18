import base64
import pandas as pd
import streamlit as st
import requests

@st.cache_data(show_spinner=False)
def get_album_info_from_id(album_link):
    # Extrait l'ID de l'album depuis le lien
    try:
        album_id = album_link.rstrip('/').split('/')[-1]
        url = f"https://api.deezer.com/album/{album_id}"
        response = requests.get(url)
        data = response.json()
        return {
            "img_url": data.get("cover_medium", "N/A"),
            "nb_tracks": data.get("nb_tracks", "N/A"),
            "fans": data.get("fans", "N/A"),
            "duration": data.get("duration", "N/A"),
            "release_date": data.get("release_date", "N/A")
        }
    except Exception:
        pass
    return None

#Function needed to use placeholder in HTML
def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def likedAlbums(file_path):
    df = pd.read_excel(file_path, sheet_name="5_favoriteAlbum")
    st.title("💿 Albums likés")
    st.markdown("---")

    albumsDict = {}
    for i in range(len(df)):
        album = df.iloc[i]["Album Title"]
        link = df.iloc[i]["Link"]
        albumsDict[album] = link

    # Barre de recherche
    search = st.text_input("🔎 Rechercher un album")
    if search:
        albumsDict = {k: v for k, v in albumsDict.items() if search.lower() in k.lower()}

    #Sort in alphabetical order
    albumsDict = dict(sorted(albumsDict.items(), key=lambda item: item[0].lower()))

    img_base64 = get_base64_image("placeholder_pics/placeholder-picture.jpg")
    placeholder = f"data:image/jpeg;base64,{img_base64}"

    #Print 4 by 4 albums with their picture and link to their Deezer page
    albums = list(albumsDict.items())
    row_items = 4
    for i in range(0, len(albums), row_items):
        cols = st.columns(row_items)
        for j, (album, link) in enumerate(albums[i:i+row_items]):
            with cols[j]:
                album_info = get_album_info_from_id(link)
                #Correct format of the link
                if not link.startswith("http"):
                    link = "https://" + link.lstrip("/")
                #If album not found, use a placeholder image and do not display the link
                if album_info == {'img_url': 'N/A', 'nb_tracks': 'N/A', 'fans': 'N/A', 'duration': 'N/A', 'release_date': 'N/A'}:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <img src="{placeholder}" alt="{album}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{album}</span>
                            </div>""",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <a href="{link}" target="_blank" style="text-decoration: none;">
                                    <img src="{album_info['img_url']}" alt="{album}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                </a>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{album}</span>
                            </div>""",
                        unsafe_allow_html=True
                    )
