# Koda paskaidrojums aizstāvēšanai

## Kā strādā projekts

`game/engine.py` satur klasi `CourierGame`. Tā glabā čūskas šūnas,
virzienu, paku, piegādes punktus un nomesto asti. Šis fails neimportē Pygame.
Čūskas galva ir saraksta `snake` pirmais elements. Šūna ir `(x, y)` pāris.

`client/main.py` klase `GameClient` lasa Pygame notikumus un zīmē kvadrātus.
`run()` mēra pagājušo laiku un nodod to `game.update(seconds)`.
Zīmēšana notiek līdz 60 kadriem sekundē, bet čūska kustas ar 7, 9 vai 11 soļiem.
`set_direction()` nepieļauj pagriezienu tieši pretējā virzienā.

`client/api_client.py` izmanto requests. Klients veic HTTP pieprasījumus
fona pavedienos un ievieto atbildi `Queue`. Galvenais cikls nolasa rindu.
Tā zīmēšana negaida lēnu serveri, un tikai galvenais pavediens maina ekrāna stāvokli.

## Pieci iespējamie jautājumi

**Kur pārbauda sadursmi?** `CourierGame.move()` aprēķina jauno galvu.
Tad pārbauda laukuma robežas, ķermeni un `obstacles`. Parastā solī pēdējais
astes posms aiziet prom, tāpēc to sadursmes pārbaudē neiekļauj.
Piegādes solī čūska aug, tāpēc pārbauda visu pašreizējo ķermeni.

**Kāpēc POST atgriež 201?** `api/main.py` dekoratorā ir `status_code=201`,
jo pieprasījums rada jaunu rezultāta ierakstu. GET tikai nolasa datus un atgriež 200.
Nederīgus laukus pārbauda Pydantic un atgriež 422.

**Kas notiek, ja serveris izslēgts?** Requests izmet savienojuma kļūdu vai
noildzes izņēmumu. `ApiClient` to pārvērš par `ApiResult(ok=False, ...)`.
Spēle parāda ziņu, nevis beidz darbu. Automātiska atkārtota sūtīšana nenotiek.

**Kā dati nonāk datubāzē?** `save_score()` saņem Pydantic objektu,
izsauc `Database.add_score()`, un sqlite3 izpilda `INSERT ... VALUES (?, ?)`.
Vārds un punkti tiek padoti atsevišķā kortežā, tāpēc apostrofs nav SQL kods.
Savienojuma transakcija saglabā izmaiņas, un `closing()` aizver savienojumu.

**Kā mainīt ātrumu vai punktus?** Ātrumi ir `CourierGame.speed` īpašībā.
Punkti ir `CourierGame.score` īpašībā, pašlaik `deliveries * 20`.
Ja maini noteikumus, atjauno arī vietnes noteikumus, Dizains.docx un testus.

## Abas mehānikas

Pakas savākšana uzstāda `carrying` un noņem paku no laukuma.
Piegāde notiek tikai tad, ja jaunā galva sakrīt ar `depots[carrying]`.
Tad piegāžu skaits palielinās, aste netiek saīsināta un parādās jauna paka.

`drop_tail()` pārbauda garumu, noņem pēdējos trīs elementus un izveido
`DroppedTail` ar termiņu `elapsed + 5`. `update()` izdzēš beigušos šķēršļus.
Pauzē `update()` uzreiz beidzas, tāpēc arī astes termiņš nevirzās.

## Ko izmēģināt pašam

Palaid serveri un spēli, piegādā trīs pakas un nomet asti.
Tad apturi serveri un pabeidz vēl vienu spēli. Apskati paziņojumu.
Atver /docs, iesūti nederīgus punktus un paskaidro atbildi 422.
Atrodi iepriekš minētās metodes un pamēģini mainīt vienu ātrumu.
