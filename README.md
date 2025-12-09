# 🏎️ Simracing Adatkezelő Rendszer

Python alapú adatkezelő rendszer szimulált simracing versenyek adataival. Generál játékosokat, versenyeket, részletes köreredményeket, menti CSV/JSON/XLSX formátumokban, támogatja az Oracle SQL betöltést, és interaktív Streamlit dashboardot biztosít.

## ✨ Főbb Funkciók

- **Faker alapú adategenerálás**: Játékosok (32 fő), versenyek (100+), köradatok ELO rating és reputáció rendszerrel
- **Több formátum támogatása**: CSV, JSON, XLSX (külön munkalapokkal, színezéssel)
- **Oracle SQL integráció**: Teljes séma létrehozás, PK/FK kapcsolatok
- **Interaktív dashboard**: Ranglista, játékos karrier, köradatok elemzése
- **Valósághű szimuláció**: Köridők, incidensek, dinamikus rating frissítések

## 🚀 Gyors Indítás

- git clone https://github.com/Baboae/adatkezelo.git
- cd adatkezelo
- pip install -r requirements.txt

**Opcionális Oracle DB (.env fájl szükséges):**

    DB_USER=felhasznaloneved
    DB_PASSWORD=jelszavad
    DB_HOST=adatbazis_szerver_cime
    DB_PORT=1521
    DB_SERVICE=adatbazis_szolgaltatod_neve

- python main.py


**A program automatikusan:**
1. Törli a korábbi eredményeket
2. Generál játékosokat, versenyeket, eredményeket
3. Ment minden formátumban (`created/` mappába)
4. Opcionálisan betölti Oracle DB-be
5. **Indítja a Streamlit dashboardot** (`http://localhost:8501`)

## 📂 Projekt Struktúra

├── main.py # 🎯 Fő futtató script
├── requirements.txt # 📦 Függőségek
├── data/
│ └── raw/ # 📊 Referencia adatok
│ ├── cars.json
│ ├── tracks.json
│ └── reference_laps.json
├── generators/ # ⚙️ Adatgenerátorok
│ ├── player_generator.py # 👥 Játékosok
│ ├── race_data_generator.py # 🏁 Versenyadatok
│ └── race_result_generator.py # 🏎️ Eredmények + ELO
├── functions/ # 🔧 I/O műveletek
│ ├── json_io.py # 📄 JSON
│ ├── csv_io.py # 📋 CSV
│ ├── xlsx_io.py # 📊 XLSX (színezés!)
│ ├── sql_handler.py # 🗄️ Oracle SQL
│ ├── clear_results.py # 🧹 Tisztítás
│ ├── unix_to_timestamp.py # ⏱️ Időformázás
│ └── unix_to_datetime.py # 📅 Dátumformázás
├── data/
│ └── basic/
│ └── model_classes.py # 🏗️ Adatmodellek
└── dashboard/ # 📈 Streamlit UI
└── app.py # 🖥️ Interaktív dashboard

## 🏆 Dashboard Funkciók

- **Global Leaderboard**: ELO/reputáció rangsor, játékos kiválasztás
- **Player Career**: Statisztikák, verseny történet, átlagos befutó hely
- **Lap Details**: Köridők, pozíciók, incidensek részletesen
- **Interaktív táblázatok**: Kattintható drill-down navigáció

## 💾 Kimeneti Fájlok

**CSV**: `created/csvs/players.csv`, `race_meta.csv`, `race_results/*.csv`  
**JSON**: `created/jsons/players.json`, `race_meta.json`, `race_results/*.json`  
**XLSX**: `created/xlsxs/players.xlsx`, `race_results/*.xlsx` (RaceResult, Participants, Laps lapok)

**XLSX speciális színezés (Participants lapon):**
- Rating/reputation változások: **zöld** (+), **piros** (-)
- Pozíció javulás: **zöld** (jobb hely), **piros** (rosszabb hely)

## 🔗 Adatkapcsolatok

- Player 1:N ParticipantResult ← N:1 RaceResult
- Player 1:N Lap ← N:1 ParticipantResult
- PK-k: user_id, race_id, (race_id, user_id, lap)


## 🔧 Technikai Részletek

- **Faker**: Többnyelvű nevek, ország-specifikus usernemek
- **ELO rating**: Dinamikus K=32 faktorral
- **Időszimuláció**: 2025.11.24-30, 14:00-01:30 versenyidőpontok
- **Technológiák**: Streamlit, AgGrid, openpyxl, oracledb
