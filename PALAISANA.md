# Projekta palaišana

Autors: Somats Bečers. Spēle darbojas atsevišķā Pygame logā,
bet FastAPI serveris saglabā rezultātus un parāda mājaslapu.

## Sagatavošana

Nepieciešams Python 3.11 vai jaunāks. Ieteicamā versija ir Python 3.12.
Pirmo reizi palaid `setup.bat`, lai izveidotu virtuālo vidi `.venv`
un uzstādītu bibliotēkas. Bibliotēku uzstādīšanai vajadzīgs internets.

## Palaišana

1. Palaid `start_server.bat` un atstāj servera logu atvērtu.
2. Palaid `start_game.bat` vai projekta saknes failu `main.py`.
3. Mājaslapu atver adresē <http://127.0.0.1:8000>.
4. API dokumentācija ir <http://127.0.0.1:8000/docs>.

## Darbs VS Code

Atver visu projekta mapi. VS Code iestatījumi izmanto
projekta `.venv/Scripts/python.exe`.

- F5 palaiž konfigurāciju **Spēle**.
- Lai palaistu serveri, sadaļā **Run and Debug** izvēlies **Serveris**.
- Izvēlnē **Terminal → Run Task** ir uzdevumi **Spēle**, **Serveris** un **Testi**.

`game/engine.py` satur noteikumus un kustību, `client/main.py` satur
logu un taustiņu apstrādi, `api/main.py` satur servera maršrutus.
Projekta saknes `main.py` palaiž spēli virtuālajā vidē.
Pārbaudes var palaist ar `.venv\Scripts\python.exe -m pytest -q`
pēc `requirements-dev.txt` bibliotēku uzstādīšanas.

## Vadība

Izvēlnē ievadi vārdu un nospied Enter. Bultiņas vai WASD vada čūsku.
P vai Esc ieslēdz pauzi. Space nomet trīs astes posmus, ja ir vismaz
septiņi posmi. Paka jāpiegādā tādas pašas krāsas rāmī.
Pēc spēles beigām sagaidi saglabāšanas paziņojumu un nospied Enter.

Pilni noteikumi, projekta uzbūve un API tabula ir failā [README.md](README.md).
