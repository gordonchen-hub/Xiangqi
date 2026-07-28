#!/usr/bin/env python
"""
Build a compact Xiangqi knowledge model from the bundled master games.

The output is consumed by game/logic.rpy. It contains:
- exact position replies, like an opening/middlegame book;
- generalized move priors, used as a learned bias when exact positions miss.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "象棋大數據"
INFO_PATH = DATA_ROOT / "gameinfo.csv"
MOVES_PATH = DATA_ROOT / "moves.csv" / "moves.csv"
OUTPUT_PATH = PROJECT_ROOT / "game" / "xq_learned_policy.json"

PIECE_CODES = {
    "K": 1,
    "A": 2,
    "E": 3,
    "H": 4,
    "R": 5,
    "C": 6,
    "P": 7,
}


def initial_board():
    board = [[0 for _ in range(9)] for _ in range(10)]
    board[0] = [-5, -4, -3, -2, -1, -2, -3, -4, -5]
    board[2][1] = -6
    board[2][7] = -6
    board[3] = [-7, 0, -7, 0, -7, 0, -7, 0, -7]
    board[9] = [5, 4, 3, 2, 1, 2, 3, 4, 5]
    board[7][1] = 6
    board[7][7] = 6
    board[6] = [7, 0, 7, 0, 7, 0, 7, 0, 7]
    return board


def board_key(board):
    return "/".join(",".join(str(cell) for cell in row) for row in board)


def move_code(move):
    return "{},{},{},{}".format(*move)


def parse_move_code(code):
    return [int(part) for part in code.split(",")]


def side_sign(side):
    return 1 if side == "red" else -1


def file_to_x(file_number, side):
    file_number = int(file_number)
    if side == "red":
        return 9 - file_number
    return file_number - 1


def x_to_file(x, side):
    if side == "red":
        return 9 - x
    return x + 1


def is_advancing(side, sy, cy):
    return cy < sy if side == "red" else cy > sy


def front_first(candidates, side):
    return sorted(candidates, key=lambda item: item[1], reverse=(side == "black"))


def is_face_to_face(board):
    red_king = None
    black_king = None

    for y in range(10):
        for x in range(9):
            if board[y][x] == 1:
                red_king = (x, y)
            elif board[y][x] == -1:
                black_king = (x, y)

    if not red_king or not black_king or red_king[0] != black_king[0]:
        return False

    x = red_king[0]
    y1, y2 = sorted([red_king[1], black_king[1]])
    for y in range(y1 + 1, y2):
        if board[y][x] != 0:
            return False

    return True


def count_obstacles(board, x1, y1, x2, y2):
    count = 0
    if x1 == x2:
        for y in range(min(y1, y2) + 1, max(y1, y2)):
            if board[y][x1] != 0:
                count += 1
    elif y1 == y2:
        for x in range(min(x1, x2) + 1, max(x1, x2)):
            if board[y1][x] != 0:
                count += 1
    return count


def is_valid_move(board, sx, sy, cx, cy):
    if not (0 <= sx < 9 and 0 <= cx < 9 and 0 <= sy < 10 and 0 <= cy < 10):
        return False

    piece = board[sy][sx]
    target = board[cy][cx]

    if piece == 0 or (sx == cx and sy == cy):
        return False
    if (piece > 0 and target > 0) or (piece < 0 and target < 0):
        return False

    abs_piece = abs(piece)
    dx = abs(cx - sx)
    dy = abs(cy - sy)
    valid = False

    if abs_piece == 1:
        valid = (
            dx + dy == 1
            and 3 <= cx <= 5
            and ((piece > 0 and cy >= 7) or (piece < 0 and cy <= 2))
        )
    elif abs_piece == 2:
        valid = (
            dx == 1
            and dy == 1
            and 3 <= cx <= 5
            and ((piece > 0 and cy >= 7) or (piece < 0 and cy <= 2))
        )
    elif abs_piece == 3:
        valid = (
            dx == 2
            and dy == 2
            and board[(sy + cy) // 2][(sx + cx) // 2] == 0
            and ((piece > 0 and cy >= 5) or (piece < 0 and cy <= 4))
        )
    elif abs_piece == 4:
        valid = (
            dx == 1
            and dy == 2
            and board[sy + (1 if cy > sy else -1)][sx] == 0
        ) or (
            dx == 2
            and dy == 1
            and board[sy][sx + (1 if cx > sx else -1)] == 0
        )
    elif abs_piece == 5:
        valid = (sx == cx or sy == cy) and count_obstacles(board, sx, sy, cx, cy) == 0
    elif abs_piece == 6:
        if sx == cx or sy == cy:
            obstacles = count_obstacles(board, sx, sy, cx, cy)
            valid = obstacles == 1 if target != 0 else obstacles == 0
    elif abs_piece == 7:
        valid = (
            dx + dy == 1
            and (
                (piece > 0 and cy <= sy and (sy < 5 or sx == cx))
                or (piece < 0 and cy >= sy and (sy > 4 or sx == cx))
            )
        )

    if not valid:
        return False

    old_target = board[cy][cx]
    board[cy][cx] = board[sy][sx]
    board[sy][sx] = 0
    illegal_face = is_face_to_face(board)
    board[sy][sx] = board[cy][cx]
    board[cy][cx] = old_target

    return not illegal_face


def legal_moves_from(board, sx, sy):
    moves = []
    for cy in range(10):
        for cx in range(9):
            if is_valid_move(board, sx, sy, cx, cy):
                moves.append((sx, sy, cx, cy))
    return moves


def source_candidates(board, side, piece_abs, qualifier):
    sign = side_sign(side)
    candidates = []

    for y in range(10):
        for x in range(9):
            if board[y][x] == sign * piece_abs:
                candidates.append((x, y))

    if qualifier.isdigit():
        x = file_to_x(qualifier, side)
        return [(cx, cy) for cx, cy in candidates if cx == x]

    if qualifier not in "+-":
        return []

    grouped = defaultdict(list)
    for x, y in candidates:
        grouped[x].append((x, y))

    selected = []
    for group in grouped.values():
        if len(group) < 2:
            continue
        ordered = front_first(group, side)
        selected.append(ordered[0] if qualifier == "+" else ordered[-1])

    if selected:
        return selected

    ordered = front_first(candidates, side)
    if not ordered:
        return []
    return [ordered[0] if qualifier == "+" else ordered[-1]]


def matches_notation(board, side, move, action, target):
    sx, sy, cx, cy = move
    piece = abs(board[sy][sx])
    target_number = int(target)

    if action == ".":
        return sy == cy and x_to_file(cx, side) == target_number

    if action not in "+-":
        return False

    advancing = is_advancing(side, sy, cy)
    if action == "+" and not advancing:
        return False
    if action == "-" and advancing:
        return False

    if piece in (1, 5, 6, 7) and sx == cx:
        return abs(cy - sy) == target_number

    return x_to_file(cx, side) == target_number


def parse_notation(board, side, notation):
    notation = notation.strip()
    if len(notation) != 4:
        return None

    piece_abs = PIECE_CODES.get(notation[0].upper())
    if not piece_abs:
        return None

    qualifier = notation[1]
    action = notation[2]
    target = notation[3]
    if target not in "123456789":
        return None

    matches = []
    for sx, sy in source_candidates(board, side, piece_abs, qualifier):
        for move in legal_moves_from(board, sx, sy):
            if matches_notation(board, side, move, action, target):
                matches.append(move)

    if len(matches) == 1:
        return matches[0]

    # A real ambiguity is safer to reject than to guess. The already replayed
    # prefix is still useful, while the uncertain suffix is ignored.
    if len(matches) > 1:
        return None

    return None


def apply_move(board, move):
    sx, sy, cx, cy = move
    board[cy][cx] = board[sy][sx]
    board[sy][sx] = 0


def mirror_board(board):
    mirrored = [[0 for _ in range(9)] for _ in range(10)]
    for y in range(10):
        for x in range(9):
            mirrored[9 - y][8 - x] = -board[y][x]
    return mirrored


def mirror_move(move):
    sx, sy, cx, cy = move
    return (8 - sx, 9 - sy, 8 - cx, 9 - cy)


def outcome_for_black(winner):
    if winner == "black":
        return 1.0
    if winner == "red":
        return -1.0
    return 0.0


def elo_weight(game):
    try:
        black_elo = int(game.get("blackELO") or 0)
        red_elo = int(game.get("redELO") or 0)
    except ValueError:
        return 1.0

    average = (black_elo + red_elo) / 2.0
    return min(2.5, max(0.75, 1.0 + (average - 1200.0) / 1000.0))


def add_stat(table, key, outcome, weight):
    stat = table[key]
    stat["count"] += 1
    stat["weight"] += weight
    stat["score_sum"] += outcome * weight


def add_example(position_stats, prior_stats, board, move, outcome, weight):
    key = board_key(board)
    code = move_code(move)
    position = position_stats[key]
    position["visits"] += 1
    position["moves"][code]["count"] += 1
    position["moves"][code]["weight"] += weight
    position["moves"][code]["score_sum"] += outcome * weight

    sx, sy, cx, cy = move
    piece = board[sy][sx]
    add_stat(prior_stats, "move:{}:{}".format(piece, code), outcome, weight)
    add_stat(prior_stats, "to:{}:{},{}".format(piece, cx, cy), outcome, weight * 0.6)
    add_stat(prior_stats, "delta:{}:{},{}".format(piece, cx - sx, cy - sy), outcome, weight * 0.35)


def compact_score(stat):
    count = stat["count"]
    weight = max(stat["weight"], 0.001)
    average = stat["score_sum"] / weight
    confidence = min(1.0, count / 24.0)
    return round((average * confidence) + math.log(count + 1.0) * 0.06, 4)


def read_games():
    games = {}
    with INFO_PATH.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            games[row["gameID"]] = row
    return games


def read_moves():
    moves = defaultdict(lambda: {"red": {}, "black": {}})
    with MOVES_PATH.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            side = row["side"]
            if side not in ("red", "black"):
                continue
            moves[row["gameID"]][side][int(row["turn"])] = row["move"]
    return moves


def build_policy(max_positions, max_moves_per_position, min_position_visits, min_prior_visits):
    games = read_games()
    games_moves = read_moves()

    position_stats = defaultdict(lambda: {"visits": 0, "moves": defaultdict(lambda: {"count": 0, "weight": 0.0, "score_sum": 0.0})})
    prior_stats = defaultdict(lambda: {"count": 0, "weight": 0.0, "score_sum": 0.0})

    parsed_games = 0
    skipped_games = 0
    parsed_moves = 0
    failed_samples = []

    for game_id, sides in games_moves.items():
        game = games.get(game_id)
        if not game:
            skipped_games += 1
            continue

        board = initial_board()
        black_outcome = outcome_for_black(game.get("winner", "draw"))
        red_as_black_outcome = -black_outcome
        weight = elo_weight(game)
        max_turn = max(
            list(sides["red"].keys() or [0]) + list(sides["black"].keys() or [0])
        )

        game_failed = False
        for turn in range(1, max_turn + 1):
            for side in ("red", "black"):
                notation = sides[side].get(turn)
                if not notation:
                    continue

                move = parse_notation(board, side, notation)
                if move is None:
                    game_failed = True
                    if len(failed_samples) < 12:
                        failed_samples.append(
                            {
                                "gameID": game_id,
                                "turn": turn,
                                "side": side,
                                "move": notation,
                                "board": board_key(board),
                            }
                        )
                    break

                if side == "black":
                    add_example(position_stats, prior_stats, board, move, black_outcome, weight)
                else:
                    add_example(
                        position_stats,
                        prior_stats,
                        mirror_board(board),
                        mirror_move(move),
                        red_as_black_outcome,
                        weight,
                    )

                apply_move(board, move)
                parsed_moves += 1

            if game_failed:
                break

        if game_failed:
            skipped_games += 1
        else:
            parsed_games += 1

    ranked_positions = sorted(
        (
            (key, value)
            for key, value in position_stats.items()
            if value["visits"] >= min_position_visits
        ),
        key=lambda item: item[1]["visits"],
        reverse=True,
    )[:max_positions]

    positions = {}
    for key, value in ranked_positions:
        ranked_moves = sorted(
            value["moves"].items(),
            key=lambda item: (compact_score(item[1]), item[1]["count"]),
            reverse=True,
        )[:max_moves_per_position]

        positions[key] = {
            "visits": value["visits"],
            "moves": [
                {
                    "move": parse_move_code(code),
                    "count": stat["count"],
                    "score": compact_score(stat),
                }
                for code, stat in ranked_moves
            ],
        }

    priors = {
        key: {
            "count": stat["count"],
            "score": compact_score(stat),
        }
        for key, stat in prior_stats.items()
        if stat["count"] >= min_prior_visits
    }

    return {
        "metadata": {
            "source": "Xiangqi bundled master-game CSV",
            "games_total": len(games),
            "games_parsed": parsed_games,
            "games_skipped": skipped_games,
            "moves_parsed": parsed_moves,
            "positions_kept": len(positions),
            "priors_kept": len(priors),
            "min_position_visits": min_position_visits,
            "min_prior_visits": min_prior_visits,
            "max_positions": max_positions,
            "max_moves_per_position": max_moves_per_position,
            "failed_samples": failed_samples,
        },
        "positions": positions,
        "priors": priors,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--max-positions", type=int, default=25000)
    parser.add_argument("--max-moves-per-position", type=int, default=5)
    parser.add_argument("--min-position-visits", type=int, default=2)
    parser.add_argument("--min-prior-visits", type=int, default=2)
    args = parser.parse_args()

    policy = build_policy(
        max_positions=args.max_positions,
        max_moves_per_position=args.max_moves_per_position,
        min_position_visits=args.min_position_visits,
        min_prior_visits=args.min_prior_visits,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(policy, handle, ensure_ascii=False, separators=(",", ":"))

    meta = policy["metadata"]
    print(
        "Wrote {path}\n"
        "Parsed {games_parsed}/{games_total} games, {moves_parsed} moves.\n"
        "Kept {positions_kept} exact positions and {priors_kept} priors.\n"
        "Skipped {games_skipped} games.".format(path=args.output, **meta)
    )


if __name__ == "__main__":
    main()
