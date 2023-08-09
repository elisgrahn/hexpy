from pieces import Bishop, King, Knight, Pawn, Queen, Rook

from hexpy import Hex, Hexigo, hexmap


def paint_board(
    hxmp: hexmap.HexMap,
    colors: tuple[tuple[float, float, float], ...],
) -> hexmap.HexMap:
    """Paints the board"""

    def paint_diagonals(
        hx: Hex,
        color: tuple[float, float, float],
    ) -> None:
        """Recursively paints diagonals"""
        hxmp[hx] = color

        for diag_hx in hx.diagonal_neighbors:
            if diag_hx in hxmp and hxmp[diag_hx] != color:
                paint_diagonals(diag_hx, color)

    diagonal_origins = (Hex.o_clock(2), Hexigo, Hex.o_clock(12))

    for origin, color in zip(diagonal_origins, colors):
        paint_diagonals(origin, color)

    return hxmp


def get_pieces() -> set[Bishop | King | Knight | Pawn | Queen | Rook]:
    """Get a set of all pieces in their starting positions"""

    # TODO want to use hexpy.hexset.new() instead!
    pieces = set()

    for team in "white", "black":
        for piece in Bishop, King, Knight, Pawn, Queen, Rook:
            # Get this teams positons for the piece

            positions = (
                piece.white_positions if team == "white" else piece.black_positions
            )

            for pos in positions:
                pieces.add(piece(pos, team))

    return pieces
