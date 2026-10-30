# Runas piezīmes

Prezentācijā ir 6 slaidi. Kopējais runas laiks ir apmēram 4 minūtes.
Pirms uzstāšanās izmēģini stāstījumu un pielāgo sarežģītākās vietas aprakstu
savai faktiskajai pieredzei.

## 1 Čūska kurjers

Apmēram 25 sekundes. Mani sauc Somats Bečers. Šis ir mans prakses projekts.
Spēle izmanto Python un Pygame. Čūska piegādā pakas un var
nomest asti. Rezultātus saglabā FastAPI serveris SQLite datubāzē.

## 2 Kā spēlēt

Apmēram 40 sekundes. Izvēlnē ievada savu vārdu. Ar bultiņām vai WASD
vada čūsku. Mazais krāsainais kvadrāts ir paka, rāmji ir piegādes punkti.
Jāizvairās no sienām un ķermeņa. P vai Esc aptur spēli. Pēc 3 un 6
piegādēm ātrums pieaug no 7 uz 9 un 11 soļiem sekundē.

## 3 Paku piegāde

Apmēram 40 sekundes. Pirmā īpašā mehānika ir krāsainu paku piegāde.
Vienlaikus var nest vienu paku. Paņemot paku, punktus vēl nesaņem.
Tā jānogādā atbilstošās krāsas rāmī. Pēc piegādes saņem 20 punktus
un vienu astes posmu. Nepareizās krāsas punktā nekas nenotiek.
Krāsainais kvadrāts uz čūskas galvas rāda savākto paku.

## 4 Astes nomešana

Apmēram 40 sekundes. Otrā mehānika ir astes nomešana. Pēc trim piegādēm
čūskai ir septiņi posmi. Ar Space nomet pēdējos trīs un paliek četri.
Pelēkie posmi piecas spēles sekundes traucē kustēties, un tajos var
ietriekties. Pauzē laiks apstājas. Čūska kļūst īsāka, bet rodas jauns šķērslis.

## 5 Serveris un mājaslapa

Apmēram 55 sekundes. Spēles beigās requests nosūta JSON ar vārdu un
punktiem uz POST /scores. FastAPI pārbauda datus ar Pydantic un saglabā
SQLite datubāzē. Veiksmīga atbilde ir 201. GET /scores/top atgriež desmit
labākās spēles. Statistikā ir spēļu skaits un labākais rezultāts.
Tas pats serveris ar Jinja veidnēm parāda tabulu, profilu un noteikumus.
Attēlā ir atsevišķas pārbaudes datubāzes rezultāti.

## 6 Sarežģītākā daļa un pārbaude

Apmēram 40 sekundes. Tehniski sarežģītākā daļa ir HTTP pieprasījumi
spēles ciklā. Ja tos izpilda galvenajā pavedienā, lēns serveris aptur
zīmēšanu. Šajā projektā pieprasījumus veic fona pavedieni un atbildes
ievieto rindā. Galvenais cikls nolasa rindu. Pieprasījumiem ir noildze.
Ar pytest pārbaudīti spēles noteikumi un API.
