"""Spēles noteikumi: čūskas kustība, pakas, punkti un sadursmes.

Šis fails glabā spēles datus. Logu un attēlus zīmē client/main.py.
"""

import random
from dataclasses import dataclass

# (x, y) ir rūtiņas koordinātas, nevis pikseļi. Piemēram, (7, 9).
# Virziens norāda izmaiņu vienā solī: RIGHT = (1, 0) palielina x par 1.
# Ekrānā y palielinās uz leju, tāpēc UP samazina y par 1.
Cell = tuple[int, int]
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
COLORS = ("red", "blue", "yellow")


@dataclass
class Parcel:
    """Paka, kas atrodas vienā laukuma šūnā."""

    position: Cell
    color: str


@dataclass
class DroppedTail:
    """Nomestās astes rūtiņas un spēles laiks, kad tām jāpazūd."""

    cells: list[Cell]
    expires_at: float


class CourierGame:
    """Viena spēles partija ar savu čūsku, pakām un punktiem."""

    def __init__(self, seed: int | None = None) -> None:
        """Sākt spēli 24 reiz 18 šūnu laukumā ar četriem posmiem."""
        self.width = 24
        self.height = 18
        # Saraksta pirmais posms snake[0] ir galva, pēdējais ir astes gals.
        self.snake: list[Cell] = [(7, 9), (6, 9), (5, 9), (4, 9)]
        # direction ir pašreizējais virziens; next_direction būs nākamajā solī.
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.turn_queued = False
        self.deliveries = 0
        # carrying ir vestās pakas krāsa. None nozīmē, ka čūska neko neved.
        # parcel ir paka uz laukuma; kamēr čūska to ved, parcel ir None.
        self.carrying: str | None = None
        self.parcel: Parcel | None = None
        # Katrai pakas krāsai ir savs piegādes punkts.
        self.depots: dict[str, Cell] = {
            "red": (2, 2),
            "blue": (21, 2),
            "yellow": (12, 15),
        }
        self.dropped_tails: list[DroppedTail] = []
        # elapsed skaita spēles sekundes; pauzes laikā tas nepalielinās.
        # accumulator krāj laiku līdz nākamajam čūskas kustības solim.
        self.elapsed = 0.0
        self.accumulator = 0.0
        self.paused = False
        self.over = False
        self.won = False
        self.message = "Savāc paku un nogādā tās krāsas punktā."
        # Ar vienādu seed testos iegūst vienādas nejaušās pakas.
        # Parastā spēlē seed ir None, tāpēc paku secība var atšķirties.
        self.random = random.Random(seed)
        self.spawn_parcel()

    @property
    def score(self) -> int:
        """Aprēķināt punktus: piegāžu skaits reiz 20."""
        # @property ļauj šo vērtību nolasīt kā game.score, bez iekavām.
        return self.deliveries * 20

    @property
    def level(self) -> int:
        """Noteikt līmeni: 0–2 piegādes → 1., 3–5 → 2., no 6 → 3."""
        # // ir dalīšana bez atlikuma; min neļauj līmenim pārsniegt 3.
        return min(3, 1 + self.deliveries // 3)

    @property
    def speed(self) -> int:
        """Atgriezt kustības ātrumu šūnās sekundē."""
        # Līmeņi sākas ar 1, bet saraksta indeksi sākas ar 0.
        return (7, 9, 11)[self.level - 1]

    @property
    def obstacles(self) -> set[Cell]:
        """Savākt visu nomesto astu rūtiņas vienā kopā sadursmju pārbaudei."""
        return {cell for tail in self.dropped_tails for cell in tail.cells}

    def spawn_parcel(self) -> None:
        """Izvēlēties jaunai pakai brīvu rūtiņu un nejaušu krāsu."""
        # Aizņemtas ir čūskas, nomesto astu un piegādes punktu rūtiņas.
        occupied = set(self.snake) | self.obstacles | set(self.depots.values())
        free = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in occupied
        ]
        # Ja brīvu rūtiņu nav, jaunu paku nevar izveidot — spēlētājs uzvar.
        if not free:
            self.parcel = None
            self.over = True
            self.won = True
            self.message = "Uzvara! Jaunai pakai vairs nav vietas."
            return
        self.parcel = Parcel(
            self.random.choice(free), self.random.choice(COLORS)
        )

    def set_direction(self, direction: Cell) -> None:
        """Atļaut vienu pagriezienu solī un nepieļaut kustību atpakaļ."""
        # Pēc viena pieņemta pagrieziena gaidām nākamo kustības soli.
        # Citādi divi ātri taustiņi ļautu čūskai uzreiz apgriezties sevī.
        if self.over or self.paused or self.turn_queued:
            return
        if direction not in (UP, DOWN, LEFT, RIGHT):
            return
        # Piemēram, virzienam RIGHT (1, 0) pretējais ir LEFT (-1, 0).
        opposite = (-self.direction[0], -self.direction[1])
        if direction == opposite or direction == self.direction:
            return
        self.next_direction = direction
        self.turn_queued = True

    def toggle_pause(self) -> None:
        """Pārslēgt pauzi: True kļūst par False un otrādi."""
        if not self.over:
            self.paused = not self.paused

    def drop_tail(self) -> bool:
        """Nomest 3 pēdējos posmus; True nozīmē, ka nomešana izdevās."""
        if self.over or self.paused:
            return False
        if len(self.snake) < 7:
            self.message = "Astes nomešanai vajag vismaz 7 posmus."
            return False
        # [-3:] paņem pēdējos 3 posmus, bet [:-3] atstāj pārējo čūsku.
        # Tāpēc vismaz 7 posmus gara čūska pēc nomešanas saglabā vismaz 4.
        cells = self.snake[-3:]
        self.snake = self.snake[:-3]
        # Nomestie posmi kļūst par šķērsli uz 5 spēles sekundēm.
        # Piemēram, ja elapsed ir 12, aste pazudīs pie elapsed = 17.
        self.dropped_tails.append(DroppedTail(cells, self.elapsed + 5.0))
        self.message = "Aste nomesta uz 5 spēles sekundēm."
        return True

    def update(self, seconds: float) -> None:
        """Apstrādāt kopš iepriekšējā kadra pagājušās sekundes."""
        if self.over or self.paused or seconds <= 0:
            return
        # remaining ir laiks, kas šajā izsaukumā vēl jāapstrādā.
        # To sadala daļās, lai arī lēnāka kadra laikā pareizi izpildītu soļus.
        remaining = seconds
        while remaining > 0 and not self.over:
            # Pie ātruma 7 viens solis ilgst 1/7 sekundes.
            # delta ir laiks līdz solim vai viss atlikušais kadra laiks.
            interval = 1 / self.speed
            delta = min(remaining, interval - self.accumulator)
            self.elapsed += delta
            self.accumulator += delta
            remaining = max(0.0, remaining - delta)
            # Atstājam tikai tās nomestās astes, kuru pazušanas laiks nav pienācis.
            self.dropped_tails = [
                tail
                for tail in self.dropped_tails
                if tail.expires_at > self.elapsed + 1e-9
            ]
            # 1e-9 ir ļoti maza pielaide, jo daļskaitļus dators noapaļo.
            # Kad sakrāts viena soļa laiks, pārvietojam čūsku.
            if self.accumulator >= interval - 1e-9:
                self.accumulator = 0.0
                self.move()

    def move(self) -> None:
        """Pārvietot čūsku par vienu rūtiņu un pārbaudīt šī soļa rezultātu."""
        self.direction = self.next_direction
        self.turn_queued = False
        x, y = self.snake[0]
        dx, dy = self.direction
        # Jaunā galva = vecās galvas vieta + izvēlētais virziens.
        head = (x + dx, y + dy)
        # Piegāde notiek, ja čūska ved paku un ieiet tās krāsas punktā.
        delivering = (
            self.carrying is not None and head == self.depots[self.carrying]
        )
        # Parastā solī astes gals aiziet prom, tāpēc tajā drīkst ieiet ar galvu.
        # Piegādes solī čūska aug, astes gals paliek un arī tas jāpārbauda.
        body = self.snake if delivering else self.snake[:-1]
        # Galvai jāpaliek laukuma robežās: x no 0 līdz 23, y no 0 līdz 17.
        if not (0 <= head[0] < self.width and 0 <= head[1] < self.height):
            self.over = True
            self.message = "Sadursme ar sienu."
            return
        if head in body or head in self.obstacles:
            self.over = True
            self.message = "Sadursme ar ķermeni vai nomesto asti."
            return
        # Pievienojam galvu saraksta sākumā. Parastā solī noņemam astes galu,
        # tāpēc garums nemainās. Piegādē asti nenoņemam — garums pieaug par 1.
        self.snake.insert(0, head)
        if not delivering:
            self.snake.pop()
        if self.parcel is not None and head == self.parcel.position:
            # Pakas savākšana vēl nedod punktus: saglabājam tikai tās krāsu.
            self.carrying = self.parcel.color
            self.parcel = None
            self.message = "Paka savākta. Atrodi atbilstošās krāsas punktu."
        if delivering:
            # Pieskaitām piegādi, iztukšojam čūskas kravu un izveidojam jaunu paku.
            self.deliveries += 1
            self.carrying = None
            self.message = "Piegāde pabeigta! +20 punkti."
            self.spawn_parcel()
