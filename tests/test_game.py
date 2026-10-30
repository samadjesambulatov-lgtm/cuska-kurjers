"""Spēles noteikumu testi bez Pygame loga izveides."""

from game.engine import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    CourierGame,
    DroppedTail,
    Parcel,
)


def test_pickup_then_correct_delivery() -> None:
    """Pakas savākšana nedod punktus, bet piegāde pagarina čūsku."""
    game = CourierGame(seed=1)
    game.parcel = Parcel((8, 9), "red")
    game.depots["red"] = (9, 9)
    game.move()
    assert game.carrying == "red" and game.parcel is None
    assert game.score == 0 and len(game.snake) == 4
    game.move()
    assert game.carrying is None and game.parcel is not None
    assert game.score == 20 and len(game.snake) == 5


def test_wrong_depot_gives_no_points() -> None:
    """Sarkanas pakas aizvešana uz zilo punktu nedod punktus."""
    game = CourierGame()
    game.carrying = "red"
    game.parcel = None
    game.depots["blue"] = (8, 9)
    game.move()
    assert game.score == 0 and game.carrying == "red"


def test_three_difficulty_levels() -> None:
    """Katra līmeņa ātrums atbilst spēles aprakstam."""
    game = CourierGame()
    for deliveries, level, speed in [
        (0, 1, 7),
        (2, 1, 7),
        (3, 2, 9),
        (5, 2, 9),
        (6, 3, 11),
        (10, 3, 11),
    ]:
        game.deliveries = deliveries
        assert (game.level, game.speed) == (level, speed)


def test_drop_requires_seven_and_keeps_four() -> None:
    """Pēc astes nomešanas vienmēr paliek vismaz četri posmi."""
    game = CourierGame()
    assert not game.drop_tail()
    game.snake = [(10 - i, 9) for i in range(7)]
    assert game.drop_tail()
    assert len(game.snake) == 4
    assert game.obstacles == {(6, 9), (5, 9), (4, 9)}
    assert not game.drop_tail()


def test_obstacle_timer_and_pause() -> None:
    """Nomestie posmi paliek piecas sekundes, un pauze aptur laiku."""
    game = CourierGame()
    game.snake = [(10 - i, 9) for i in range(7)]
    game.drop_tail()
    game.toggle_pause()
    before = list(game.snake)
    game.update(100)
    assert game.elapsed == 0 and game.snake == before
    assert game.obstacles
    game.toggle_pause()
    # Droši apbrauc taisnstūri, gaidot nomestās astes pazušanu.
    for direction, steps in [
        (RIGHT, 8),
        (UP, 6),
        (LEFT, 8),
        (DOWN, 6),
        (RIGHT, 6),
    ]:
        game.set_direction(direction)
        game.update(steps / 7)
    assert not game.over and game.elapsed < 5 and game.obstacles
    game.update(1 / 7)
    assert abs(game.elapsed - 5) < 1e-8 and not game.obstacles


def test_obstacle_and_wall_collisions() -> None:
    """Sadursme ar sienu vai nomesto asti beidz spēli."""
    game = CourierGame()
    game.dropped_tails = [DroppedTail([(8, 9)], 5)]
    game.move()
    assert game.over
    game = CourierGame()
    game.snake = [(23, 9), (22, 9), (21, 9), (20, 9)]
    game.move()
    assert game.over


def test_body_collision_and_departing_tail() -> None:
    """Ķermenis bloķē kustību, bet pēdējā aizejošā šūna ir droša."""
    game = CourierGame()
    game.snake = [(3, 3), (3, 4), (4, 4), (4, 3)]
    game.move()
    assert not game.over and game.snake[0] == (4, 3)
    game = CourierGame()
    game.snake = [(3, 3), (3, 4), (4, 4), (4, 3), (5, 3)]
    game.move()
    assert game.over


def test_turn_queue_forbids_instant_reverse() -> None:
    """Vairāki taustiņi starp soļiem nevar apgriezt kustības virzienu."""
    game = CourierGame()
    game.set_direction(LEFT)
    assert game.next_direction == RIGHT
    game.set_direction(UP)
    game.set_direction(LEFT)
    game.move()
    assert game.direction == UP and game.snake[0] == (7, 8)


def test_spawn_avoids_objects_and_full_board_wins() -> None:
    """Pakas neparādās aizņemtās šūnās, un pilns laukums dod uzvaru."""
    game = CourierGame(seed=2)
    for _ in range(30):
        game.spawn_parcel()
        assert game.parcel.position not in set(game.snake) | set(
            game.depots.values()
        )
    game.snake = [
        (x, y) for y in range(game.height) for x in range(game.width)
    ]
    game.spawn_parcel()
    assert game.won and game.over and game.parcel is None
