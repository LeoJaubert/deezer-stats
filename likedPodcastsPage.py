import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import requests

#API call to obtain infos about podcast
@st.cache_data(show_spinner = False)
def getPodcastInfoFromId(podcast_link):
    try:
        podcast_id = podcast_link.rstrip('/').split('/')[-1]
        url = f"https://api.deezer.com/podcast/{podcast_id}"
        response = requests.get(url, timeout = 10)
        data = response.json()

        fans = int(data.get("fans", 0))

        return {
            "img_url": data["picture_medium"],
            "fans_formatted": f"{fans:,}",
            "description": data["description"],
            "url": url
        }

    except (requests.exceptions.RequestException, KeyError, ValueError):
        return None

#Do all API requests in bulk
@st.cache_data(show_spinner = False)
def getAllPodcastsInfo(podcast_links: tuple):
    def fetch(podcast_link):
        return podcast_link, getPodcastInfoFromId(podcast_link)

    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch, link): link for link in podcast_links}
        for future in as_completed(futures):
            link, info = future.result()
            results[link] = info
    return results

#Function needed to use placeholder in HTML
def getBase64Image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

#Popup appearing when clicking on the button containing infos about podcast
@st.dialog("Détails du podcast")
def showPodcastModal(podcast, link, podcast_info):
    st.markdown(f"""
        # 🗨 {podcast}
        🧑 **Fans** : {podcast_info['fans_formatted']}\n
        🔠 **Description** : {podcast_info['description']} 
    """, unsafe_allow_html = True)

    st.markdown(
        f"""
        <a href="{link}" target="_blank"
        style="
            display:inline-block;
            padding:10px 16px;
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

#--------------Code starts here--------------#
def likedPodcasts(sheet):
    df = sheet
    st.title("💬 Podcasts likés", anchor = False)
    st.markdown("---")

    podcasts_dict = {}
    for i in range(len(df)):
        podcast = df.iloc[i]["Podcast Name"]
        link = df.iloc[i]["Link"]
        podcasts_dict[podcast] = link

    #Search bar
    search = st.text_input(f"🔎 Rechercher parmi les {len(df)} podcasts :")
    if search:
        podcasts_dict = {k: v for k, v in podcasts_dict.items() if search.lower() in k.lower()}
    #Sort in alphabetical order
    podcasts_dict = dict(sorted(podcasts_dict.items(), key=lambda item: item[0].lower()))

    img_base64 = getBase64Image("pictures/placeholder-picture.jpg")
    placeholder = f"data:image/jpeg;base64,{img_base64}"

    #Print 4 by 4 podcasts with their picture and link to their Deezer page
    podcasts = list(podcasts_dict.items())
    all_links = tuple(link for _, link in podcasts)
    podcasts_info = getAllPodcastsInfo(all_links)
    row_items = 4
    for i in range(0, len(podcasts), row_items):
        cols = st.columns(row_items)
        for j, (podcast, link) in enumerate(podcasts[i:i+row_items]):
            with cols[j]:
                podcast_info = podcasts_info.get(link)
                #Correct format of the link
                if not link.startswith("http"):
                    link = "https://" + link.lstrip("/")
                #If podcast not found, use a placeholder image and do not display the link
                if podcast_info is None:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <img src="{placeholder}" alt="{podcast}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{podcast}</span>
                            </div>""",
                        unsafe_allow_html = True
                    )
                else:
                    st.markdown(
                        f"""
                        <div style="display:flex; flex-direction:column; align-items:center;">
                            <img src="{podcast_info['img_url']}"
                                width="70"
                                style="border-radius:8px; box-shadow:0 2px 8px #0001; margin-bottom:8px">
                        </div>
                        """,
                        unsafe_allow_html = True
                    )

                    #Button with podcast name
                    if st.button(
                        podcast,
                        use_container_width = True,
                        type = "primary"
                    ):
                        showPodcastModal(podcast, link, podcast_info)
