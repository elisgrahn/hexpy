from hexpy import Hex, hexmap

hexboard: hexmap.HexMap
turn: int = 1


def update() -> None:
    "Update the board, removing old possible positons and creating the new ones"

    def update_in_direction(pos: Hex, dir: Hex, ctr: int = 0) -> None:
        "Recursively update from position in direction"

        if pos in hexboard.hexes():
            # Check the next in the direction
            if hexboard[pos] == -turn:
                update_in_direction(pos + dir, dir, ctr + 1)

            elif ctr > 0 and hexboard[pos] == 0:
                hexboard[pos] = 2 * turn

    # Reset all possible positions of the other player
    for position in hexboard.get_hexes(-2 * turn):
        hexboard[position] = 0

    # Get all positions belonging to current player
    for position in hexboard.get_hexes(turn):
        for i, neighbor in enumerate(position.neighbors()):
            # Check that it is in the map/board
            if neighbor in hexboard:
                update_in_direction(neighbor, position.direction(i))


def flip(position: Hex) -> None:
    "Flip the board from the position"

    def flip_in_direction(pos: Hex, dir: Hex, ctr: int = 0) -> None:
        "Recursively flip from position in direction"

        if pos in hexboard:
            # Check the next in the direction
            if hexboard[pos] == -turn:
                flip_in_direction(pos + dir, dir, ctr + 1)

            elif ctr > 0 and hexboard[pos] == turn:
                for to_flip in position.linedraw_to(pos):
                    hexboard[to_flip] = turn

    hexboard[position] = turn

    for i, neighbor in enumerate(position.neighbors()):
        flip_in_direction(neighbor, position.direction(i))


def start() -> None:
    "Call this to start the game"

    update()


def check() -> bool:
    "Check if the current player can place anything"

    possible_moves = tuple(hexboard.get_hexes(2 * turn))

    if len(possible_moves) == 0:
        return False

    return True


def make_move(position: Hex) -> bool:
    global turn

    if position in hexboard.get_hexes(2 * turn):
        # Flip pieces around the clicked hex
        flip(position)

        turn *= -1

        # Prepare the board for the next turn
        update()

        if not check():
            print("can't place")

            turn *= -1
            update()

        return True

    return False
