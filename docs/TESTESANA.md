# Projekta pārbaude

Automātiskie testi atrodas `tests/`. Tie izmanto savas pagaidu datubāzes
un nemaina spēlētāja saglabātos rezultātus.

## Manuālā pārbaude

1. Palaid serveri un spēli. Izvēlnē sagaidi servera statusu un ievadi vārdu.
2. Savāc paku. Punktiem jāpaliek 0. Aizved pareizajā punktā: jābūt 20 punktiem.
3. Pārbaudi, ka nepareizās krāsas punkts nedod punktus.
4. Pēc 3 piegādēm jābūt 2. līmenim un 9 soļiem sekundē.
5. Nospied Space. No 7 posmiem jāpaliek 4, trīs pelēkiem posmiem jāpaliek laukumā.
6. Ieslēdz pauzi uz vairāk nekā 5 sekundēm. Nomestajai astei jāpaliek.
7. Turpini spēli. Pēc atlikušajām spēles sekundēm šķērslim jāpazūd.
8. Pēc 6 piegādēm jābūt 3. līmenim un 11 soļiem sekundē.
9. Iebrauc sienā. Sagaidi saglabāšanas paziņojumu un pārlādē mājaslapu.
10. Atver sava vārda saiti, pārbaudi spēļu skaitu un labāko rezultātu.
11. Pārstartē serveri. Rezultātiem jāpaliek datubāzē.
12. Apturi serveri, izvēlnē nospied F5 un pārbaudi, ka spēli joprojām var sākt.
13. Pabeidz spēli bez servera. Logam jāreaģē, jārāda kļūdas paziņojums.

## API pārbaude ar /docs

`POST /scores`: parasts vārds un 40 punkti dod 201. Tukšs JSON, negatīvi
punkti un vārds ar 25 rakstzīmēm dod 422 un netiek saglabāti.
`GET /scores/top` dod 200. Nezināma spēlētāja statistika dod 404.
Lai pārbaudītu saglabāšanu, nosūti nulles rezultātu un tad apskati profilu.

Ekrānuzņēmumi mapē `docs/` ir iegūti ar atsevišķu pārbaudes datubāzi.
Pakas piegādes un nomestās astes attēli rāda īstās spēles loģikas stāvokļus.
Prezentācijas tabulā redzamie vārdi un rezultāti ir pārbaudes dati.
