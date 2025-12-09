**Adatkezelő programok fejlesztése - Szabó Benedek**

Ez a python projekt egy fiktív verseny szimulátor nyilvántarásához generál le adatokat,
melyeket több formátumban ment. (CSV, JSON, XLSX)

## Mit csinál a program ❓❓❓

- Faker API segítségével generál szintetikus adatokat két vagy több kapcsolódó adattípushoz.
- Az adatok többféle formátumban menthetők (CSV, JSON, XLSX), és visszaolvashatók ezekből
  (nincs mind implementálva, tesztelve, de a program "functions" mappájában megtalálható az összes) 
- Lehetőség van az adatok Oracle SQL adatbázisba történő feltöltésére is (Lásd: Előfeltételek 3. bekezdés). 

A generált adatok többek között a Player, Race_Data, Lap, stb... amelyek között kapcsolat áll fenn.

## Hogyan használd?

Klónozd le a repót, végezz el minden előfeltételt, majd futtasd a main.py állományt.
Az adatok legenerálása eltarthat egy kis ideig, ez függ attól hogy hogyan paraméterezed
valamint attól hogy feltöltöd-e az eredményt adatbázisba vagy sem.

git clone https://github.com/Baboae/adatkezelo.git

## ELŐFELTÉTELEK:

1. Telepítsd a függőségeket 🛠 :
- Nyisd meg a konzolt, majd vidd be a következőt:
  pip install -r requirements.txt

2. Paraméterezés ⚙ (opcionális):

- A generáló függvény több paramétert kap: a generálandó játékosok 👥 (alap: 32), versenyek 🏁 (alap: 1000),
min/max körök 🚗💨 (alap: 3, 10) számát.
Ezeket a kódban a következő kommentek alatti változókban található számok átírásával lehetséges:
      # generálandó játékosok száma. 
      # generálandó versenyek száma.
      # generálandó minimum, maximum körök száma.
        
3. SQL kapcsolat:
Feltételek:
- A .env fájl megléte a program gyökér mappájában.
  Példa a .env fájl tartalmára:

    DB_USER=felhasznaloneved
    DB_PASSWORD=jelszavad
    DB_HOST=adatbazis_szerver_cime
    DB_PORT=1521
    DB_SERVICE=adatbazis_szolgaltatod_neve

- Az sql kapcsolat létrehozásának engedélyezése a kódban.
  Ezt a következő komment alatti változó értékének "True"-ra változtatásával teheted meg:
        # DB betöltés (opcionális)
