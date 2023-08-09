from typing import Literal, Optional

from pyrsistent import v

from hexpy import Hex, Hexigo, hexmap


def mirror(hxmp: hexmap.HexMap) -> hexmap.HexMap:
    """Return the HexMap mirrored over axis"""

    # return hexmap.fromkeys(hx.reflected("q") for hx in hxmp)

    return hxmp.transform(lambda hx: hx.reflected("q"))


Hex.flat_layout(10)


class Piece:
    white_positions: hexmap.HexMap = hexmap.new()
    moves: hexmap.HexMap = hexmap.new()

    def __new__(cls, pos: Hex, team: Literal["white", "black"]):  # -> Self:
        """Creating the black positions and moves here before initializing"""

        cls.black_positions: hexmap.HexMap = mirror(cls.white_positions)

        return object.__new__(cls)

    def __init__(self, pos: Hex, team: Literal["white", "black"]):
        self._pos = pos
        self.team = team
        # self.image = ?

    def __repr__(self):
        return f"{self.__class__.__name__}({self.pos}, {self.team})"

    @property
    def movemap(self) -> hexmap.HexMap:
        """This provides a base implementation, the pieces that need dynamic moves should override this property

        For instance if the piece is a pawn, we need to firstly check if it is at the start position
        however for a Rook it doesn't matter where it is, it can always move in a straight line
        """
        return self.moves + self.pos

    @property
    def pos(self) -> Hex:
        """Returns the position of the piece"""
        return self._pos

    @pos.setter
    def pos(self, new_pos: Hex):
        """Moves the piece to the new position"""
        if new_pos - self.pos in self.moves:
            self._pos = new_pos
        else:
            raise ValueError(f"{new_pos} is not a valid move")

    @pos.deleter
    def pos(self):
        """Same as the kill method"""
        del self._pos

    def move(self, new_pos: Hex):
        """Moves the piece to the new position"""
        self.pos = new_pos

    def kill(self) -> None:
        """Removes the piece from the board"""
        del self.pos


class Rook(Piece):
    white_positions = hexmap.fromkeys((Hex(-3, 5), Hex(3, 2)))

    moves = hexmap.fromkeys(
        (hx * step for step in range(1, 11) for hx in Hex.hexcompass)
    )

    # def possible_moves(self, board: hexmap.HexMap, pieces: set[Hex]) -> hexmap.HexMap:

    #     for hx in Hex.hexcompass:

    #         if hx + self.pos in pieces.pos:

    #         if hx in board:
    #             if board[hx] == self.team:
    #                 pass
    #             else:
    #                 pass
    #         else:
    #             pass

    #     board & held.movemap


class Bishop(Piece):
    white_positions = hexmap.fromkeys((Hex(0, 5), Hex(0, 4), Hex(0, 3)))

    moves = hexmap.fromkeys(
        (hx * step for step in range(1, 6) for hx in Hexigo.diagonals)
    )


class Queen(Piece):
    white_positions = hexmap.fromkeys(Hex(-1, 5))

    moves = Rook.moves | Bishop.moves


class King(Piece):
    white_positions = hexmap.fromkeys(Hex(1, 4))

    moves = hexmap.fromkeys(Hex.hexclock)


class Knight(Piece):
    white_positions = hexmap.fromkeys((Hex(-2, 5), Hex(2, 3)))

    moves = hexmap.hexagon(3, hollow=True)
    moves.pop((hx * 3 for hx in Hex.hexclock))


class Pawn(Piece):
    white_positions = hexmap.fromkeys(
        (
            Hex(-4, 5),
            Hex(-3, 4),
            Hex(-2, 3),
            Hex(-1, 2),
            Hex(0, 1),
            Hex(1, 1),
            Hex(2, 1),
            Hex(3, 1),
            Hex(4, 1),
        )
    )
    # TODO I NEED A HexSet class for this instead!
    white_moves = hexmap.fromkeys(
        (Hex.compass("NW"), Hex.compass("N"), Hex.compass("NE"))
    )
    # black_moves = mirror(white_moves)
    black_moves = hexmap.fromkeys(
        (Hex.compass("SW"), Hex.compass("S"), Hex.compass("SE"))
    )

    @property
    def at_start(self):
        """Checks if we are in a starting postions, i.e. we are allowed to move two places forward"""

        if self.team == "white":
            return self.pos in self.white_positions

        else:
            return self.pos in self.black_positions

    @property
    def moves(self) -> hexmap.HexMap:
        """For Pawns this is a property, since the moves are not symmetrical for white and black"""

        if not self.at_start:
            return self.white_moves if self.team == "white" else self.black_moves

        dynamic_move = hexmap.fromkeys(
            2 * Hex.compass("N" if self.team == "white" else "S")
        )

        static_moves = self.white_moves if self.team == "white" else self.black_moves

        return static_moves | dynamic_move


if __name__ == "__main__":
    from hexpy import Hex, Hexigo

    # print(Rook.moves)
    # Pawn(Hex(0, 1), "white").moves.plot(title="Pawn")
    # Rook.moves.plot(title="Rook")
    # Bishop.moves.plot(title="Bishop")
    # Queen.moves.plot(title="Queen")
    # King.moves.plot(title="King")
    # Knight.moves.plot(title="Knight")
    # def get_moves_in_direction(
    #     steps: int,
    #     hx: Hex,
    #     direction: Optional[Hex] = None,
    #     moves: hexmap.HexMap = hexmap.new(),
    # ) -> hexmap.HexMap:
    #     """"""
    #     if direction is None:
    #         direction = hx
    #     moves.insert(hx)
    #     if steps == 0:
    #         return moves
    #     return get_moves_in_direction(steps - 1, hx + direction, direction, moves)
    # print(get_moves_in_direction(5, Hex(1, 0)))
