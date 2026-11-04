"""Vienkārša Pygame izvēlne, laukums, pauze un rezultātu ekrāns."""

from queue import Empty, Queue
from threading import Thread

import pygame
from game.engine import DOWN, LEFT, RIGHT, UP, CourierGame
from game.names import MAX_NAME_LENGTH, validate_name

from client.api_client import ApiClient, ApiResult

CELL = 26
BOARD_X, BOARD_Y = 22, 82
WINDOW = (940, 650)
BACKGROUND = (213, 230, 225)
TEXT = (36, 64, 63)
ACCENT = (37, 91, 89)
INPUT = (237, 242, 226)
BORDER = (115, 151, 137)
BOARD = (232, 239, 213)
GRID = (202, 216, 187)
COLOR = {
    "red": (200, 45, 45),
    "blue": (45, 85, 200),
    "yellow": (172, 128, 0),
}
COLOR_NAME = {"red": "sarkana", "blue": "zila", "yellow": "dzeltena"}


class GameClient:
    """Nolasīt taustiņus, zīmēt spēli un saņemt servera atbildes."""

    def __init__(self) -> None:
        """Sagatavot fontus, logu, izvēlni un rezultātu pieprasījumu."""
        pygame.init()
        pygame.display.set_caption("Čūska kurjers")
        self.screen = pygame.display.set_mode(WINDOW)
        self.font = pygame.font.SysFont("arial", 20)
        self.small = pygame.font.SysFont("arial", 16)
        self.title = pygame.font.SysFont("arial", 32, bold=True)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"
        self.name = ""
        self.round_name = ""
        self.error = ""
        self.game = CourierGame()
        self.api = ApiClient()
        self.responses: Queue[tuple[str, int, ApiResult]] = Queue()
        self.top: list[dict] = []
        self.top_message = "Ielādē rezultātus..."
        self.save_message = ""
        self.loading_top = False
        self.saving = False
        self.round_id = 0
        pygame.key.start_text_input()
        self.load_top()

    def text(
        self,
        value: str,
        x: int,
        y: int,
        small: bool = False,
        color: tuple[int, int, int] = TEXT,
    ) -> None:
        """Uzzīmēt teksta rindu ar parasto vai mazo fontu."""
        font = self.small if small else self.font
        self.screen.blit(font.render(value, True, color), (x, y))

    def load_top(self) -> None:
        """Pieprasīt rezultātus fona pavedienā, neapturot logu."""
        if self.loading_top:
            return
        self.loading_top = True
        self.top_message = "Ielādē rezultātus..."

        def work() -> None:
            self.responses.put(("top", 0, self.api.load_top()))

        Thread(target=work, daemon=True).start()

    def send_score(self) -> None:
        """Vienu reizi nosūtīt pabeigtās spēles rezultātu."""
        name, score, round_id = self.round_name, self.game.score, self.round_id
        self.saving = True
        self.save_message = "Saglabā rezultātu..."

        def work() -> None:
            self.responses.put(
                ("save", round_id, self.api.save_score(name, score))
            )

        Thread(target=work, daemon=True).start()

    def collect_responses(self) -> None:
        """Atjaunot ekrāna stāvokli ar saņemtajām servera atbildēm."""
        while True:
            try:
                kind, round_id, result = self.responses.get_nowait()
            except Empty:
                break
            if kind == "top":
                self.loading_top = False
                self.top = result.scores or []
                self.top_message = result.message
            elif round_id == self.round_id:
                self.saving = False
                self.save_message = result.message

    def start_game(self) -> None:
        """Pārbaudīt ievadīto vārdu un sākt jaunu spēli."""
        try:
            self.name = validate_name(self.name)
        except ValueError as error:
            self.error = str(error)
            return
        self.round_name = self.name
        self.round_id += 1
        self.game = CourierGame()
        self.state = "playing"
        self.error = ""
        self.save_message = ""
        self.saving = False
        pygame.key.stop_text_input()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Pārvērst Pygame notikumus izvēlnes vai spēles darbībās."""
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.WINDOWFOCUSLOST and self.state == "playing":
            if not self.game.paused:
                self.game.toggle_pause()
        if self.state == "menu":
            if event.type == pygame.TEXTINPUT:
                self.name = (self.name + event.text)[:MAX_NAME_LENGTH]
                self.error = ""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif event.key == pygame.K_RETURN:
                    self.start_game()
                elif event.key == pygame.K_F5:
                    self.load_top()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            return
        if event.type != pygame.KEYDOWN:
            return
        if self.state == "over":
            if event.key == pygame.K_RETURN and not self.saving:
                self.state = "menu"
                pygame.key.start_text_input()
                self.load_top()
            return
        directions = {
            pygame.K_UP: UP,
            pygame.K_w: UP,
            pygame.K_DOWN: DOWN,
            pygame.K_s: DOWN,
            pygame.K_LEFT: LEFT,
            pygame.K_a: LEFT,
            pygame.K_RIGHT: RIGHT,
            pygame.K_d: RIGHT,
        }
        if event.key in directions:
            self.game.set_direction(directions[event.key])
        elif event.key in (pygame.K_p, pygame.K_ESCAPE):
            self.game.toggle_pause()
        elif event.key == pygame.K_SPACE:
            self.game.drop_tail()

    def draw_menu(self) -> None:
        """Uzzīmēt vārda ievadi, vadības norādes un labākos rezultātus."""
        self.screen.blit(
            self.title.render("Čūska kurjers", True, ACCENT), (30, 28)
        )
        self.text("Spēlētāja vārds (1–24 rakstzīmes):", 30, 100)
        pygame.draw.rect(self.screen, INPUT, (30, 138, 400, 42))
        pygame.draw.rect(self.screen, BORDER, (30, 138, 400, 42), 1)
        self.text(self.name + "_", 40, 145)
        self.text(self.error, 30, 190, small=True, color=(165, 30, 30))
        for i, line in enumerate(
            [
                "Enter — sākt spēli",
                "Bultiņas / WASD — kustība",
                "P / Esc — pauze",
                "Space — nomest 3 astes posmus",
                "Piegāde pareizā punktā: +20 punkti",
                "F5 — atjaunot topu; Esc — iziet",
            ]
        ):
            self.text(line, 30, 245 + i * 34)
        self.text("Labākie 10 rezultāti", 520, 100)
        for i, row in enumerate(self.top):
            self.text(
                f"{i + 1}. {row['name']} — {row['score']}",
                520,
                143 + i * 32,
                small=True,
            )
        if not self.top and not self.loading_top:
            self.text("Nav saglabātu rezultātu.", 520, 145, small=True)
        self.text(self.top_message, 30, 555, small=True)
        self.text(
            "Serveris un mājaslapa: " + self.api.base_url, 30, 585, small=True
        )
        if self.save_message:
            self.text(self.save_message, 30, 615, small=True)

    def cell_rect(self, cell: tuple[int, int]) -> pygame.Rect:
        """Pārvērst laukuma koordinātas zīmējamā taisnstūrī."""
        return pygame.Rect(
            BOARD_X + cell[0] * CELL, BOARD_Y + cell[1] * CELL, CELL, CELL
        )

    def draw_board(self) -> None:
        """Uzzīmēt šūnas, piegādes rāmjus un informācijas kolonnu."""
        game = self.game
        self.text(
            f"Čūska kurjers    Punkti: {game.score}    Līmenis: {game.level}",
            22,
            22,
        )
        self.text(f"Spēlētājs: {self.round_name}", 22, 51, small=True)
        board = pygame.Rect(
            BOARD_X, BOARD_Y, game.width * CELL, game.height * CELL
        )
        pygame.draw.rect(self.screen, BOARD, board)
        for x in range(game.width + 1):
            px = BOARD_X + x * CELL
            pygame.draw.line(
                self.screen, GRID, (px, BOARD_Y), (px, board.bottom)
            )
        for y in range(game.height + 1):
            py = BOARD_Y + y * CELL
            pygame.draw.line(
                self.screen, GRID, (BOARD_X, py), (board.right, py)
            )
        pygame.draw.rect(self.screen, BORDER, board, 1)
        for color, cell in game.depots.items():
            pygame.draw.rect(
                self.screen,
                COLOR[color],
                self.cell_rect(cell).inflate(-4, -4),
                4,
            )
        for tail in game.dropped_tails:
            for cell in tail.cells:
                pygame.draw.rect(
                    self.screen,
                    (135, 135, 135),
                    self.cell_rect(cell).inflate(-2, -2),
                )
        for i, cell in enumerate(game.snake):
            color = (35, 105, 45) if i == 0 else (57, 144, 64)
            pygame.draw.rect(
                self.screen, color, self.cell_rect(cell).inflate(-2, -2)
            )
        if game.parcel:
            pygame.draw.rect(
                self.screen,
                COLOR[game.parcel.color],
                self.cell_rect(game.parcel.position).inflate(-12, -12),
            )
        if game.carrying:
            pygame.draw.rect(
                self.screen,
                COLOR[game.carrying],
                self.cell_rect(game.snake[0]).inflate(-12, -12),
            )
        sx = 673
        for i, line in enumerate(
            [
                f"Piegādes: {game.deliveries}",
                f"Ātrums: {game.speed} soļi/s",
                f"Astes posmi: {len(game.snake)}",
                "",
                "Paka: " + COLOR_NAME.get(game.carrying, "nav"),
                "",
                "Mazs kvadrāts = paka",
                "Rāmis = piegādes punkts",
                "Pelēks = nomestā aste",
                "",
                "Bultiņas / WASD: kustība",
                "P / Esc: pauze",
                "Space: nomest asti",
            ]
        ):
            self.text(line, sx, 90 + i * 28, small=True)
        self.text(game.message, 22, 570, small=True)
        self.text(
            "Astes nomešanai vajag 7 posmus. Paliek vismaz 4.",
            22,
            601,
            small=True,
        )
        if game.paused or self.state == "over":
            overlay = pygame.Surface((WINDOW[0], WINDOW[1]), pygame.SRCALPHA)
            overlay.fill((*BACKGROUND, 235))
            self.screen.blit(overlay, (0, 0))
            heading = (
                "Pauze"
                if game.paused
                else ("Uzvara!" if game.won else "Spēle beigusies")
            )
            self.screen.blit(
                self.title.render(heading, True, ACCENT), (230, 220)
            )
            if game.paused:
                self.text("P vai Esc — turpināt", 230, 280)
            else:
                self.text(f"{self.round_name}: {game.score} punkti", 230, 275)
                self.text(game.message, 230, 315, small=True)
                self.text(self.save_message, 230, 350, small=True)
                if not self.saving:
                    self.text("Enter — atgriezties izvēlnē", 230, 395)

    def run(self) -> None:
        """Zīmēt līdz 60 kadriem sekundē, kustību uzticot spēles loģikai."""
        while self.running:
            seconds = min(self.clock.tick(60) / 1000, 0.25)
            for event in pygame.event.get():
                self.handle_event(event)
            self.collect_responses()
            if self.state == "playing":
                self.game.update(seconds)
                if self.game.over:
                    self.state = "over"
                    self.send_score()
            self.screen.fill(BACKGROUND)
            if self.state == "menu":
                self.draw_menu()
            else:
                self.draw_board()
            pygame.display.flip()
        pygame.quit()


def main() -> None:
    """Palaist spēles logu ar komandu python -m client.main."""
    GameClient().run()


if __name__ == "__main__":
    main()
