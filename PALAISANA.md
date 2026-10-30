# Projekta palaišana

Autors: Somats Bečers. Spēle darbojas atsevišķā Pygame logā,
bet FastAPI serveris saglabā rezultātus un parāda mājaslapu.

## Palaišana šajā datorā

Virtuālā vide `.venv` jau ir sagatavota ar Python 3.12.

1. Palaid `start_server.bat` un atstāj servera logu atvērtu.
2. Palaid `start_game.bat` vai korenes failu `main.py`.
3. Mājaslapu atver adresē http://127.0.0.1:8000.
4. API dokumentācija ir http://127.0.0.1:8000/docs.

Pārnesot projektu uz citu datoru, instalē Python 3.12 un vispirms
palaid `setup.bat`. Bibliotēku uzstādīšanai vajadzīgs internets.

## Darbs VS Code

Atver visu mapi `C:\projects\spele`. Projektā ir saglabāti VS Code
iestatījumi, kas izmanto `.venv/Scripts/python.exe`.

- F5 palaiž konfigurāciju **Spēle**.
- Lai palaistu serveri, sadaļā **Run and Debug** izvēlies **Serveris**.
- Izvēlnē **Terminal → Run Task** ir uzdevumi **Spēle**, **Serveris** un **Testi**.

`game/engine.py` satur noteikumus un kustību, `client/main.py` satur
logu un taustiņu apstrādi, `api/main.py` satur servera maršrutus.
Korenes `main.py` tikai palaiž spēli pareizajā virtuālajā vidē.
Pārbaudes var palaist ar `.venv\Scripts\python.exe -m pytest -q`.

## Vadība

Izvēlnē ievadi vārdu un nospied Enter. Bultiņas vai WASD vada čūsku.
P vai Esc ieslēdz pauzi. Space nomet trīs astes posmus, ja ir vismaz
septiņi posmi. Paka jāpiegādā tādas pašas krāsas rāmī.
Pēc spēles beigām sagaidi saglabāšanas paziņojumu un nospied Enter.

## Apraksts un prezentācija

`README.md` satur noteikumus, palaišanas norādes un API tabulu.
`docs/AIZSTAVESANA.md` paskaidro kodu aizstāvēšanai.
`Prezentacija.pdf` satur sešus slaidus, bet runas piezīmes ir
`docs/PREZENTACIJAS_RUNA.md`.

Vecā virtuālā vide, sākotnējā faila kopija un agrākās instrukcijas
ir saglabātas `.backup/`. Šī mape un `.venv/` ir paslēptas VS Code
failu kokā un netiek pievienotas Git.

Privātā GitHub repozitorija izveide, skolotāja uzaicināšana un darba
iesniegšana Moodle un Mykoob jāveic ar savu kontu.
