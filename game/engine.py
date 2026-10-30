"""Kustība, sadursmes, piegādes un nomestā aste bez Pygame."""

import random
from dataclasses import dataclass

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
    """Trīs nomestie posmi un to pazušanas laiks."""

    cells: list[Cell]
    expires_at: float


class CourierGame:
    """Glabāt un atjaunot vienas spēles stāvokli."""

    def __init__(self, seed: int | None = None) -> None:
        """Sākt spēli 24 reiz 18 šūnu laukumā ar četriem posmiem."""
        self.width = 24
        self.height = 18
        self.snake: list[Cell] = [(7, 9), (6, 9), (5, 9), (4, 9)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.turn_queued = False
        self.deliveries = 0
        self.carrying: str | None = None
        self.parcel: Parcel | None = None
        self.depots: dict[str, Cell] = {
            "red": (2, 2),
            "blue": (21, 2),
            "yellow": (12, 15),
        }
        self.dropped_tails: list[DroppedTail] = []
        self.elapsed = 0.0
        self.accumulator = 0.0
        self.paused = False
        self.over = False
        self.won = False
        self.message = "Savāc paku un nogādā tās krāsas punktā."
        self.random = random.Random(seed)
        self.spawn_parcel()

    @property
    def score(self) -> int:
        """Piešķirt divdesmit punktus par katru piegādi."""
        return self.deliveries * 20

    @property
    def level(self) -> int:
        """Palielināt grūtību pēc trim un sešām piegādēm."""
        return min(3, 1 + self.deliveries // 3)

    @property
    def speed(self) -> int:
        """Atgriezt kustības ātrumu šūnās sekundē."""
        return (7, 9, 11)[self.level - 1]

    @property
    def obstacles(self) -> set[Cell]:
        """Apkopot šūnas, kuras aizņem nomestās astes."""
        return {cell for tail in self.dropped_tails for cell in tail.cells}

    def spawn_parcel(self) -> None:
        """Novietot paku brīvā šūnā vai piešķirt uzvaru."""
        occupied = set(self.snake) | self.obstacles | set(self.depots.values())
        free = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in occupied
        ]
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
        if self.over or self.paused or self.turn_queued:
            return
        if direction not in (UP, DOWN, LEFT, RIGHT):
            return
        opposite = (-self.direction[0], -self.direction[1])
        if direction == opposite or direction == self.direction:
            return
        self.next_direction = direction
        self.turn_queued = True

    def toggle_pause(self) -> None:
        """Apturēt vai turpināt spēli."""
        if not self.over:
            self.paused = not self.paused

    def drop_tail(self) -> bool:
        """Nomest trīs posmus uz piecām sekundēm, atstājot vismaz četrus."""
        if self.over or self.paused:
            return False
        if len(self.snake) < 7:
            self.message = "Astes nomešanai vajag vismaz 7 posmus."
            return False
        cells = self.snake[-3:]
        self.snake = self.snake[:-3]
        self.dropped_tails.append(DroppedTail(cells, self.elapsed + 5.0))
        self.message = "Aste nomesta uz 5 spēles sekundēm."
        return True

    def update(self, seconds: float) -> None:
        """Atjaunot spēles laiku un kustēties ar pašreizējo ātrumu."""
        if self.over or self.paused or seconds <= 0:
            return
        # Laiku atjauno pa soļiem, lai taimeri darbotos arī pie liela dt.
        remaining = seconds
        while remaining > 0 and not self.over:
            interval = 1 / self.speed
            delta = min(remaining, interval - self.accumulator)
            self.elapsed += delta
            self.accumulator += delta
            remaining = max(0.0, remaining - delta)
            self.dropped_tails = [
                tail
                for tail in self.dropped_tails
                if tail.expires_at > self.elapsed + 1e-9
            ]
            if self.accumulator >= interval - 1e-9:
                self.accumulator = 0.0
                self.move()

    def move(self) -> None:
        """Veikt soli, pārbaudīt sadursmes un apstrādāt paku."""
        self.direction = self.next_direction
        self.turn_queued = False
        x, y = self.snake[0]
        dx, dy = self.direction
        head = (x + dx, y + dy)
        delivering = (
            self.carrying is not None and head == self.depots[self.carrying]
        )
        # Pēdējā astes šūna atbrīvojas, ja šajā solī čūska neaug.
        body = self.snake if delivering else self.snake[:-1]
        if not (0 <= head[0] < self.width and 0 <= head[1] < self.height):
            self.over = True
            self.message = "Sadursme ar sienu."
            return
        if head in body or head in self.obstacles:
            self.over = True
            self.message = "Sadursme ar ķermeni vai nomesto asti."
            return
        self.snake.insert(0, head)
        if not delivering:
            self.snake.pop()
        if self.parcel is not None and head == self.parcel.position:
            self.carrying = self.parcel.color
            self.parcel = None
            self.message = "Paka savākta. Atrodi atbilstošās krāsas punktu."
        if delivering:
            self.deliveries += 1
            self.carrying = None
            self.message = "Piegāde pabeigta! +20 punkti."
            self.spawn_parcel()
