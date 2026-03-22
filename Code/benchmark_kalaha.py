import csv
import os
import time
import io
import contextlib
from dataclasses import dataclass
from itertools import combinations
from statistics import mean

import matplotlib.pyplot as plt

from Kalah import KalahGame
from KalahaAI import KalahaAI


@dataclass(frozen=True)
class AIConfig:
    name: str
    depth: int
    pruning_name: str
    eval_name: str

    def build_ai(self):
        pruning_map = {
            "minimax": KalahaAI.minimax,
            "alpha-beta": KalahaAI.minimax_ab,
        }

        eval_map = {
            "simple": KalahaAI.evaluate_Simple,
            "medium": KalahaAI.evaluate_Medium,
            "advanced": KalahaAI.evaluate_Adv,
        }

        return KalahaAI(
            depth=self.depth,
            pruning=pruning_map[self.pruning_name],
            Heuristic=eval_map[self.eval_name],
        )


def get_store_indices(game: KalahGame):
    """
    Returns:
        player0_store_index, player1_store_index
    """
    return game.Player0End, game.Player1End


def get_winner_from_scores(game: KalahGame):
    """
    Returns:
        0 if player 0 wins
        1 if player 1 wins
        -1 if draw
    """
    p0_store, p1_store = get_store_indices(game)
    p0_score = game.board[p0_store]
    p1_score = game.board[p1_store]

    if p0_score > p1_score:
        return 0
    elif p1_score > p0_score:
        return 1
    return -1


def safe_matchup_name(ai_a: AIConfig, ai_b: AIConfig):
    return f"{ai_a.name}_vs_{ai_b.name}".replace(" ", "_")


def normalized_matchup_label(ai_name_a: str, ai_name_b: str):
    first, second = sorted([ai_name_a, ai_name_b])
    return f"{first} vs {second}"


def play_single_game(game_id, ai_player0: AIConfig, ai_player1: AIConfig, pits, stones, move_writer, quiet=False):
    """
    Runs one full AI-vs-AI game and returns a dict with summary data.
    """
    if quiet:
        with contextlib.redirect_stdout(io.StringIO()):
            game = KalahGame(pits, stones)
    else:
        game = KalahGame(pits, stones)
    game.ai = None
    game.endGame = False

    ai0 = ai_player0.build_ai()
    ai1 = ai_player1.build_ai()

    move_number = 0
    move_times_p0 = []
    move_times_p1 = []
    total_game_start = time.perf_counter()

    while not game.endGame:
        current_player = 0 if game.CurrentPlayerIs0 else 1
        current_ai = ai0 if current_player == 0 else ai1
        current_ai_name = ai_player0.name if current_player == 0 else ai_player1.name

        game.ComputerIs0 = game.CurrentPlayerIs0

        legal_moves = game.getLegalMoves()

        t0 = time.perf_counter()
        chosen_move = current_ai.chooseMove(game)
        t1 = time.perf_counter()

        if chosen_move is None or chosen_move not in legal_moves:
            raise RuntimeError(
                f"Invalid move from AI '{current_ai_name}' in game {game_id}, move {move_number}: "
                f"chosen_move={chosen_move}, legal_moves={legal_moves}, "
                f"current_player={current_player}, board={game.board}"
            )

        move_time = t1 - t0

        if current_player == 0:
            move_times_p0.append(move_time)
        else:
            move_times_p1.append(move_time)

        extra_turn = game.makeMove(chosen_move, print_board=False)

        move_writer.writerow({
            "game_id": game_id,
            "move_number": move_number,
            "player": current_player,
            "ai_name": current_ai_name,
            "depth": current_ai.depth,
            "algorithm": ai_player0.pruning_name if current_player == 0 else ai_player1.pruning_name,
            "evaluation": ai_player0.eval_name if current_player == 0 else ai_player1.eval_name,
            "legal_moves_count": len(legal_moves),
            "chosen_move": chosen_move,
            "move_time_sec": round(move_time, 6),
            "extra_turn": int(extra_turn),
            "board_state_after_move": str(game.board),
        })

        move_number += 1

    total_game_time = time.perf_counter() - total_game_start

    p0_store, p1_store = get_store_indices(game)
    p0_score = game.board[p0_store]
    p1_score = game.board[p1_store]
    winner = get_winner_from_scores(game)

    if winner == 0:
        winner_name = ai_player0.name
    elif winner == 1:
        winner_name = ai_player1.name
    else:
        winner_name = "Draw"

    return {
        "game_id": game_id,
        "player0_ai": ai_player0.name,
        "player1_ai": ai_player1.name,
        "player0_depth": ai_player0.depth,
        "player1_depth": ai_player1.depth,
        "player0_algorithm": ai_player0.pruning_name,
        "player1_algorithm": ai_player1.pruning_name,
        "player0_evaluation": ai_player0.eval_name,
        "player1_evaluation": ai_player1.eval_name,
        "winner": winner_name,
        "winner_side": winner,
        "player0_score": p0_score,
        "player1_score": p1_score,
        "score_diff_p0_minus_p1": p0_score - p1_score,
        "moves_played": move_number,
        "avg_move_time_player0_sec": round(mean(move_times_p0), 6) if move_times_p0 else 0.0,
        "avg_move_time_player1_sec": round(mean(move_times_p1), 6) if move_times_p1 else 0.0,
        "total_game_time_sec": round(total_game_time, 6),
    }


def summarize_results(game_results, ai_configs):
    """
    Builds a summary structure for:
    - overall AI win counts
    - average move times
    - matchup summaries
    """
    overall = {
        ai.name: {
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "games": 0,
            "scores": [],
            "avg_move_times": [],
        }
        for ai in ai_configs
    }

    matchup_summary = {}

    for row in game_results:
        p0 = row["player0_ai"]
        p1 = row["player1_ai"]
        key = normalized_matchup_label(p0, p1)

        p0_is_first = (p0 == key.split(" vs ")[0])

        if key not in matchup_summary:
            matchup_summary[key] = {
                "matchup": key,
                "games": 0,
                "ai_first": key.split(" vs ")[0],
                "ai_second": key.split(" vs ")[1],
                "wins_first_ai": 0,
                "wins_second_ai": 0,
                "draws": 0,
                "scores_first": [],
                "scores_second": [],
                "avg_game_time": [],
                "avg_move_times_first": [],
                "avg_move_times_second": [],
            }

        matchup_summary[key]["games"] += 1

        if p0_is_first:
            matchup_summary[key]["scores_first"].append(row["player0_score"])
            matchup_summary[key]["scores_second"].append(row["player1_score"])
            matchup_summary[key]["avg_move_times_first"].append(row["avg_move_time_player0_sec"])
            matchup_summary[key]["avg_move_times_second"].append(row["avg_move_time_player1_sec"])
        else:
            matchup_summary[key]["scores_first"].append(row["player1_score"])
            matchup_summary[key]["scores_second"].append(row["player0_score"])
            matchup_summary[key]["avg_move_times_first"].append(row["avg_move_time_player1_sec"])
            matchup_summary[key]["avg_move_times_second"].append(row["avg_move_time_player0_sec"])

        matchup_summary[key]["avg_game_time"].append(row["total_game_time_sec"])

        overall[p0]["games"] += 1
        overall[p1]["games"] += 1
        overall[p0]["scores"].append(row["player0_score"])
        overall[p1]["scores"].append(row["player1_score"])
        overall[p0]["avg_move_times"].append(row["avg_move_time_player0_sec"])
        overall[p1]["avg_move_times"].append(row["avg_move_time_player1_sec"])

        if row["winner_side"] == 0:
            if p0_is_first:
                matchup_summary[key]["wins_first_ai"] += 1
            else:
                matchup_summary[key]["wins_second_ai"] += 1
            overall[p0]["wins"] += 1
            overall[p1]["losses"] += 1
        elif row["winner_side"] == 1:
            if p0_is_first:
                matchup_summary[key]["wins_second_ai"] += 1
            else:
                matchup_summary[key]["wins_first_ai"] += 1
            overall[p1]["wins"] += 1
            overall[p0]["losses"] += 1
        else:
            matchup_summary[key]["draws"] += 1
            overall[p0]["draws"] += 1
            overall[p1]["draws"] += 1

    overall_rows = []
    for ai_name, stats in overall.items():
        overall_rows.append({
            "ai_name": ai_name,
            "games": stats["games"],
            "wins": stats["wins"],
            "losses": stats["losses"],
            "draws": stats["draws"],
            "win_rate": round(stats["wins"] / stats["games"], 4) if stats["games"] else 0.0,
            "avg_score": round(mean(stats["scores"]), 4) if stats["scores"] else 0.0,
            "avg_move_time_sec": round(mean(stats["avg_move_times"]), 6) if stats["avg_move_times"] else 0.0,
        })

    matchup_rows = []
    for _, stats in matchup_summary.items():
        matchup_rows.append({
            "matchup": stats["matchup"],
            "games": stats["games"],
            "first_ai": stats["ai_first"],
            "second_ai": stats["ai_second"],
            "wins_first_listed_ai": stats["wins_first_ai"],
            "wins_second_listed_ai": stats["wins_second_ai"],
            "draws": stats["draws"],
            "avg_score_first_listed_ai": round(mean(stats["scores_first"]), 4),
            "avg_score_second_listed_ai": round(mean(stats["scores_second"]), 4),
            "avg_game_time_sec": round(mean(stats["avg_game_time"]), 6),
            "avg_move_time_first_listed_ai_sec": round(mean(stats["avg_move_times_first"]), 6),
            "avg_move_time_second_listed_ai_sec": round(mean(stats["avg_move_times_second"]), 6),
        })

    return overall_rows, matchup_rows


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_overall_win_rates(overall_rows, output_dir):
    names = [row["ai_name"] for row in overall_rows]
    win_rates = [row["win_rate"] for row in overall_rows]

    plt.figure(figsize=(10, 6))
    plt.bar(names, win_rates)
    plt.title("Overall Win Rate by AI Configuration")
    plt.ylabel("Win Rate")
    plt.xlabel("AI Configuration")
    plt.ylim(0, 1)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "overall_win_rates.png"), dpi=200)
    plt.close()


def plot_average_move_times(overall_rows, output_dir):
    names = [row["ai_name"] for row in overall_rows]
    times = [row["avg_move_time_sec"] for row in overall_rows]

    plt.figure(figsize=(10, 6))
    plt.bar(names, times)
    plt.title("Average Move Time by AI Configuration")
    plt.ylabel("Seconds")
    plt.xlabel("AI Configuration")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "average_move_times.png"), dpi=200)
    plt.close()


def plot_average_scores(overall_rows, output_dir):
    names = [row["ai_name"] for row in overall_rows]
    scores = [row["avg_score"] for row in overall_rows]

    plt.figure(figsize=(10, 6))
    plt.bar(names, scores)
    plt.title("Average Final Score by AI Configuration")
    plt.ylabel("Average Score")
    plt.xlabel("AI Configuration")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "average_scores.png"), dpi=200)
    plt.close()


def plot_matchup_results(matchup_rows, output_dir):
    labels = [row["matchup"] for row in matchup_rows]
    wins_a = [row["wins_first_listed_ai"] for row in matchup_rows]
    wins_b = [row["wins_second_listed_ai"] for row in matchup_rows]
    draws = [row["draws"] for row in matchup_rows]

    x = list(range(len(labels)))

    plt.figure(figsize=(12, 7))
    plt.bar(x, wins_a, label="First listed AI wins")
    plt.bar(x, draws, bottom=wins_a, label="Draws")
    bottoms = [wins_a[i] + draws[i] for i in range(len(x))]
    plt.bar(x, wins_b, bottom=bottoms, label="Second listed AI wins")

    plt.title("Matchup Results")
    plt.ylabel("Number of Games")
    plt.xlabel("Matchup")
    plt.xticks(x, labels, rotation=25, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "matchup_results.png"), dpi=200)
    plt.close()


def run_benchmark(
    ai_configs,
    pits=6,
    stones=4,
    games_per_matchup=10,
    output_dir="benchmark_results",
    quiet=True,
):
    os.makedirs(output_dir, exist_ok=True)

    if games_per_matchup % 2 != 0:
        print(
            f"Warning: games_per_matchup={games_per_matchup} is odd; "
            f"increasing to {games_per_matchup + 1} so each AI starts equally often."
        )
        games_per_matchup += 1

    print(
        "Warning: this benchmark is deterministic; repeated games with the same setup "
        "are not statistically independent samples."
    )

    games_csv = os.path.join(output_dir, "game_results.csv")
    moves_csv = os.path.join(output_dir, "move_results.csv")
    summary_csv = os.path.join(output_dir, "overall_summary.csv")
    matchup_csv = os.path.join(output_dir, "matchup_summary.csv")

    game_results = []
    game_id = 0

    move_fieldnames = [
        "game_id",
        "move_number",
        "player",
        "ai_name",
        "depth",
        "algorithm",
        "evaluation",
        "legal_moves_count",
        "chosen_move",
        "move_time_sec",
        "extra_turn",
        "board_state_after_move",
    ]

    with open(moves_csv, "w", newline="", encoding="utf-8") as mf:
        move_writer = csv.DictWriter(mf, fieldnames=move_fieldnames)
        move_writer.writeheader()

        for ai_a, ai_b in combinations(ai_configs, 2):
            print(f"Running matchup: {ai_a.name} vs {ai_b.name}")

            for i in range(games_per_matchup):
                if i % 2 == 0:
                    player0_ai = ai_a
                    player1_ai = ai_b
                else:
                    player0_ai = ai_b
                    player1_ai = ai_a

                result = play_single_game(
                    game_id=game_id,
                    ai_player0=player0_ai,
                    ai_player1=player1_ai,
                    pits=pits,
                    stones=stones,
                    move_writer=move_writer,
                    quiet=quiet,
                )

                game_results.append(result)
                print(
                    f"  Game {game_id}: "
                    f"{result['player0_ai']} ({result['player0_score']}) vs "
                    f"{result['player1_ai']} ({result['player1_score']}) -> "
                    f"{result['winner']}"
                )
                game_id += 1

    game_fieldnames = [
        "game_id",
        "player0_ai",
        "player1_ai",
        "player0_depth",
        "player1_depth",
        "player0_algorithm",
        "player1_algorithm",
        "player0_evaluation",
        "player1_evaluation",
        "winner",
        "winner_side",
        "player0_score",
        "player1_score",
        "score_diff_p0_minus_p1",
        "moves_played",
        "avg_move_time_player0_sec",
        "avg_move_time_player1_sec",
        "total_game_time_sec",
    ]

    write_csv(games_csv, game_results, game_fieldnames)

    overall_rows, matchup_rows = summarize_results(game_results, ai_configs)

    overall_fieldnames = [
        "ai_name",
        "games",
        "wins",
        "losses",
        "draws",
        "win_rate",
        "avg_score",
        "avg_move_time_sec",
    ]

    matchup_fieldnames = [
        "matchup",
        "games",
        "first_ai",
        "second_ai",
        "wins_first_listed_ai",
        "wins_second_listed_ai",
        "draws",
        "avg_score_first_listed_ai",
        "avg_score_second_listed_ai",
        "avg_game_time_sec",
        "avg_move_time_first_listed_ai_sec",
        "avg_move_time_second_listed_ai_sec",
    ]

    write_csv(summary_csv, overall_rows, overall_fieldnames)
    write_csv(matchup_csv, matchup_rows, matchup_fieldnames)

    plot_overall_win_rates(overall_rows, output_dir)
    plot_average_move_times(overall_rows, output_dir)
    plot_average_scores(overall_rows, output_dir)
    plot_matchup_results(matchup_rows, output_dir)

    print("\nBenchmark complete.")
    print(f"Saved files in: {output_dir}")
    print(f"- {games_csv}")
    print(f"- {moves_csv}")
    print(f"- {summary_csv}")
    print(f"- {matchup_csv}")
    print(f"- overall_win_rates.png")
    print(f"- average_move_times.png")
    print(f"- average_scores.png")
    print(f"- matchup_results.png")


if __name__ == "__main__":
    ai_configs = [
        AIConfig(
            name="D2_Minimax_Simple",
            depth=2,
            pruning_name="minimax",
            eval_name="simple",
        ),
        AIConfig(
            name="D4_AlphaBeta_Simple",
            depth=4,
            pruning_name="alpha-beta",
            eval_name="simple",
        ),
        AIConfig(
            name="D4_AlphaBeta_Medium",
            depth=4,
            pruning_name="alpha-beta",
            eval_name="medium",
        ),
        AIConfig(
            name="D6_AlphaBeta_Advanced",
            depth=6,
            pruning_name="alpha-beta",
            eval_name="advanced",
        ),
    ]

    run_benchmark(
        ai_configs=ai_configs,
        pits=6,
        stones=4,
        games_per_matchup=10,
        output_dir="benchmark_results"
    )