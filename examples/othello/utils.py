from hexpy import Hex, hexmap

turn: int = 1


def update(hxmp: hexmap.HexMap) -> None:
    "Update the board, removing old possible positons and creating the new ones"

    def update_in_direction(pos: Hex, dir: Hex, ctr: int = 0) -> None:
        "Recursively update from position in direction"

        if pos in hxmp.hexes():
            # Check the next in the direction
            if hxmp[pos] == -turn:
                update_in_direction(pos + dir, dir, ctr + 1)

            elif ctr > 0 and hxmp[pos] == 0:
                hxmp[pos] = 2 * turn

    # Reset all possible positions of the other player
    for position in hxmp.get_hexes(-2 * turn):
        hxmp[position] = 0

    # Get all positions belonging to current player
    for position in hxmp.get_hexes(turn):
        for i, neighbor in position.direct_neighbors.items():
            # Check that it is in the map/board
            if neighbor in hxmp:
                update_in_direction(neighbor, Hex.o_clock(i))


def flip(hxmp: hexmap.HexMap, position: Hex) -> None:
    "Flip the board from the position"

    def flip_in_direction(pos: Hex, dir: Hex, ctr: int = 0) -> None:
        "Recursively flip from position in direction"

        if pos in hxmp:
            # Check the next in the direction
            if hxmp[pos] == -turn:
                flip_in_direction(pos + dir, dir, ctr + 1)

            elif ctr > 0 and hxmp[pos] == turn:
                for to_flip in position.linedraw(pos):
                    hxmp[to_flip] = turn

    hxmp[position] = turn

    for i, neighbor in position.direct_neighbors.items():
        flip_in_direction(neighbor, Hex.o_clock(i))


def start(hxmp: hexmap.HexMap) -> None:
    "Call this to start the game"

    update(hxmp)


def check(hxmp: hexmap.HexMap) -> bool:
    "Check if the current player can place anything"

    possible_moves = tuple(hxmp.get_hexes(2 * turn))

    return bool(possible_moves)


def make_move(hxmp: hexmap.HexMap, position: Hex) -> bool:
    global turn

    if position in hxmp.get_hexes(2 * turn):
        # Flip pieces around the clicked hex
        flip(hxmp, position)

        turn *= -1

        # Prepare the board for the next turn
        update(hxmp)

        if not check(hxmp):
            turn *= -1
            update(hxmp)

        return True

    return False
