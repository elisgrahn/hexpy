from __future__ import annotations

import os.path as osp
from typing import Literal, Optional

import pygame as p

from hexpy import Hex, Hexigo, hexmap


def mirror(hxmp: hexmap.HexMap) -> hexmap.HexMap:
    """Return the HexMap mirrored over axis"""

    # return hexmap.fromkeys(hx.reflected("q") for hx in hxmp)

    return hxmp.transform(lambda hx: hx.reflected("q"))


def opponent(team: str) -> str:
    """Return the opponent of the given team"""
    return "black" if team == "white" else "white"


Hex.flat_layout(10)


class Piece:
    white_positions: hexmap.HexMap = hexmap.new()
    moves: hexmap.HexMap = hexmap.new()
    images: dict[Literal["white", "black"], p.Surface] = {}
    rects: dict[Literal["white", "black"], p.Rect] = {}

    def __new__(cls, pos: Hex, team: Literal["white", "black"]):  # -> Self:
        """Creating the black positions and moves here before initializing"""

        cls.black_positions: hexmap.HexMap = mirror(cls.white_positions)

        identifer = f"{team}-{cls.__name__.lower()}"
        cls.images[identifer], cls.rects[identifer] = cls.load_image(team)

        return object.__new__(cls)

    def __init__(self, pos: Hex, team: Literal["white", "black"]):
        self._pos = pos
        self.team = team
        # self.image = ?

    @classmethod
    def load_image(cls, team: Literal["white", "black"]) -> None:
        """Loads the image and rect for the piece of the given team"""

        img_path = f"{osp.dirname(__file__)}/pieces-basic-png/{team}-{cls.__name__.lower()}.png"
        hex_size = Hex.hexlayout.size

        image = p.image.load(img_path).convert_alpha()
        image = p.transform.scale(image, hex_size * 1.5)
        rect = image.get_rect()

        return image, rect

    @property
    def image(self) -> p.Surface:
        """Returns the image for the piece"""
        return self.images[f"{self.team}-{self.__class__.__name__.lower()}"]

    @property
    def rect(self) -> p.Rect:
        """Returns the image rect for the piece"""
        return self.rects[f"{self.team}-{self.__class__.__name__.lower()}"]

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
        self._pos = new_pos

    def move(self, new_pos: Hex):
        """Moves the piece to the new position"""
        self.pos = new_pos

    def possible_moves(
        self,
        board: hexmap.HexMap,
        pieces: dict[str, set[Piece]],
    ) -> hexmap.HexMap:
        """Returns the possible moves for a piece at the given position"""

        def allowed_move(pos: Hex) -> bool:
            """Checks if the move is allowed"""
            return pos in board & self.movemap and pos not in team_positions

        team_positions = {piece.pos for piece in pieces[self.team]}
        opponent_positions = {piece.pos for piece in pieces[opponent(self.team)]}

        visited = set()

        for direction in Hex.hexclock:
            steps = 1
            new_pos = self.pos + direction

            while new_pos not in visited and allowed_move(new_pos):
                visited.add(new_pos)

                if new_pos in opponent_positions:
                    break

                steps += 1
                new_pos = self.pos + steps * direction

        return hexmap.fromkeys(visited)


class Rook(Piece):
    white_positions = hexmap.fromkeys((Hex(-3, 5), Hex(3, 2)))

    moves = hexmap.fromkeys(
        (hx * step for step in range(1, 11) for hx in Hex.hexcompass)
    )


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

    def possible_moves(
        self,
        board: hexmap.HexMap,
        pieces: dict[str, set[Piece]],
    ) -> hexmap.HexMap:
        """Returns the possible moves for a Knight at the given position"""

        def allowed_move(pos: Hex) -> bool:
            """Checks if the move is allowed"""
            return pos in board and pos not in team_positions

        team_positions = {piece.pos for piece in pieces[self.team]}

        visited = set()

        for new_pos in self.movemap:
            if allowed_move(new_pos):
                visited.add(new_pos)

        return hexmap.fromkeys(visited)


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

    def possible_moves(
        self,
        board: hexmap.HexMap,
        pieces: dict[str, set[Piece]],
    ) -> hexmap.HexMap:
        """Returns the possible moves for a piece at the given position"""

        def allowed_move(pos: Hex) -> bool:
            """Checks if the move is allowed"""
            return pos not in team_positions | opponent_positions

        team_positions = {piece.pos for piece in pieces[self.team]}
        opponent_positions = {piece.pos for piece in pieces[opponent(self.team)]}

        visited = set()

        moves = self.white_moves if self.team == "white" else self.black_moves

        for move in moves:
            new_pos = self.pos + move

            if new_pos in board:
                if move in {Hex.compass("N"), Hex.compass("S")}:
                    
                    if allowed_move(new_pos):
                        visited.add(new_pos)

                        new_pos = self.pos + 2 * move

                        # The special double move
                        if (
                            self.at_start
                            and allowed_move(new_pos)
                        ):
                            visited.add(new_pos)

                elif new_pos in opponent_positions:
                    visited.add(new_pos)

        return hexmap.fromkeys(visited)


# if __name__ == "__main__":
# from hexpy import Hex, Hexigo
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
