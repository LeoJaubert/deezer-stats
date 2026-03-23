# Deezer Stats

![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3+-blue?logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b?logo=streamlit&logoColor=white) ![GitHub repo size](https://img.shields.io/github/repo-size/LeoJaubert/deezer-stats)


> Visualisez vos statistiques d'écoute Deezer — artistes, albums, morceaux et bien plus — à partir de vos données personnelles exportées.

---

## Fonctionnalités

- **Artistes & albums les plus écoutés**
- **Morceaux favoris** et tendances d'écoute
- **Artistes, albums & playlists likés**
- **Profil complet de l'utilisateur**
- Plein d'autres statistiques détaillées

---

## Installation

### 1. Exporter vos données Deezer

Rendez-vous dans les paramètres de votre compte Deezer via PC → *Paramètres du compte* → *Mes informations* → *Mes données personnelles*. Vous recevrez un fichier Excel par email.

### 2. Cloner le dépôt

```bash
git clone https://github.com/LeoJaubert/deezer-stats.git
cd deezer-stats
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
streamlit run main.py
```

L'application s'ouvre automatiquement dans votre navigateur à l'adresse `http://localhost:8501`.

---

## Stack technique

- [Python 3.8+](https://www.python.org/)
- [Streamlit](https://streamlit.io/) — interface web
- [Pandas](https://pandas.pydata.org/) — traitement des données
- [NumPy](https://numpy.org/) — calculs numériques
- [Altair](https://altair-viz.github.io/) — visualisations graphiques
- [Requests](https://requests.readthedocs.io/) — appels API

---

## Contribuer

Les contributions sont les bienvenues ! Pour proposer une amélioration :

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/ma-feature`)
3. Committez vos changements (`git commit -m 'feat: ajout de X'`)
4. Poussez la branche (`git push origin feature/ma-feature`)
5. Ouvrez une Pull Request

N'hésitez pas à ouvrir une [issue](https://github.com/LeoJaubert/deezer-stats/issues) pour signaler un bug ou suggérer une fonctionnalité.

---

## Licence

Ce projet est distribué sous licence [MIT](LICENSE) — libre d'utilisation, de modification et de distribution avec attribution.
