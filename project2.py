"""
GUI Tic-Tac-Toe using Tkinter (single-window layout).

- Play With : Computer / Player 2
- Select    : X / O
- Start the game : Yes (Player 1 starts) / No (Computer or Player 2 starts)
- Board is managed with a Python dictionary {1..9: ' ' | 'X' | 'O'}
- Unbeatable computer: win -> block -> best move (minimax on board copies)
- Separate functions for: position availability, win check, draw check
- Tkinter message boxes show the result and ask to play another game
"""

import tkinter as tk
from tkinter import messagebox

WIN_LINES = [
    (1, 2, 3), (4, 5, 6), (7, 8, 9),   # rows
    (1, 4, 7), (2, 5, 8), (3, 6, 9),   # columns
    (1, 5, 9), (3, 5, 7),              # diagonals
]
MOVE_ORDER = [5, 1, 3, 7, 9, 2, 4, 6, 8]   # center, corners, then sides


# ----------------------------------------------------------------------
# Board helpers (dictionary based)
# ----------------------------------------------------------------------
def new_board():
    return {pos: " " for pos in range(1, 10)}


def is_space_free(board, pos):
    """5a. Check the availability of a selected position."""
    return board[pos] == " "


def is_winner(board, letter):
    """5b. Check a win situation for the given letter."""
    return any(all(board[p] == letter for p in line) for line in WIN_LINES)


def is_draw(board):
    """5c. Check game draw (board full and nobody has won)."""
    return all(board[p] != " " for p in board) and \
        not is_winner(board, "X") and not is_winner(board, "O")


def board_full(board):
    return all(board[p] != " " for p in board)


# ----------------------------------------------------------------------
# Computer AI
# ----------------------------------------------------------------------
def minimax(board, turn, comp, human, depth):
    """Score a position from the computer's point of view."""
    if is_winner(board, comp):
        return 10 - depth
    if is_winner(board, human):
        return depth - 10
    if board_full(board):
        return 0

    scores = []
    for pos in MOVE_ORDER:
        if is_space_free(board, pos):
            trial = board.copy()
            trial[pos] = turn
            nxt = human if turn == comp else comp
            scores.append(minimax(trial, nxt, comp, human, depth + 1))
    return max(scores) if turn == comp else min(scores)


def get_computer_move(board, comp, human):
    # 1) Computer move in every free place on a copy -> pick a winning place
    for pos in MOVE_ORDER:
        if is_space_free(board, pos):
            trial = board.copy()
            trial[pos] = comp
            if is_winner(trial, comp):
                return pos
    # 2) "Player" move in every free place on a copy -> block the winning place
    for pos in MOVE_ORDER:
        if is_space_free(board, pos):
            trial = board.copy()
            trial[pos] = human
            if is_winner(trial, human):
                return pos
    # 3) No immediate win/block: center, then corners, then sides, chosen by
    #    minimax so the computer can never be beaten and always tries to win.
    best_score, best_pos = None, None
    for pos in MOVE_ORDER:
        if is_space_free(board, pos):
            trial = board.copy()
            trial[pos] = comp
            score = minimax(trial, human, comp, human, 1)
            if best_score is None or score > best_score:
                best_score, best_pos = score, pos
    return best_pos


# ----------------------------------------------------------------------
# GUI
# ----------------------------------------------------------------------
class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        root.title("Tic-Tac-Toe")
        root.resizable(False, False)

        self.mode = tk.StringVar(value="computer")
        self.letter = tk.StringVar(value="X")
        self.start_me = tk.StringVar(value="yes")

        self.board = new_board()
        self.game_over = True
        self.vs_computer = True
        self.p1, self.p2, self.current = "X", "O", "X"

        font = ("Arial", 11)

        # Row 0: Play With
        tk.Label(root, text="Play With", font=font).grid(row=0, column=0, padx=6, pady=3)
        tk.Radiobutton(root, text="Computer", variable=self.mode, value="computer",
                       font=font).grid(row=0, column=1, sticky="w")
        tk.Radiobutton(root, text="Player 2", variable=self.mode, value="player",
                       font=font).grid(row=0, column=2, sticky="w")

        # Row 1: Select letter
        tk.Label(root, text="Select", font=font).grid(row=1, column=0, padx=6, pady=3)
        tk.Radiobutton(root, text="X", variable=self.letter, value="X",
                       font=font).grid(row=1, column=1, sticky="w")
        tk.Radiobutton(root, text="O", variable=self.letter, value="O",
                       font=font).grid(row=1, column=2, sticky="w")

        # Row 2: Start the game?
        tk.Label(root, text="Start the game", font=font).grid(row=2, column=0, padx=6, pady=3)
        tk.Radiobutton(root, text="Yes", variable=self.start_me, value="yes",
                       font=font).grid(row=2, column=1, sticky="w")
        tk.Radiobutton(root, text="No", variable=self.start_me, value="no",
                       font=font).grid(row=2, column=2, sticky="w")

        # Row 3: Start button
        tk.Button(root, text="start", width=8, height=2, font=font,
                  command=self.start_game).grid(row=3, column=2, columnspan=2,
                                                sticky="e", padx=8, pady=6)

        # Status line
        self.status = tk.Label(root, text="Choose options and press start", font=font)
        self.status.grid(row=4, column=0, columnspan=4, pady=(0, 4))

        # Rows 5-7: the board (gray buttons)
        self.buttons = {}
        for pos in range(1, 10):
            b = tk.Button(root, text="", width=8, height=3, bg="gray50",
                          font=("Arial", 20, "bold"), state="disabled",
                          disabledforeground="white",
                          command=lambda p=pos: self.on_click(p))
            b.grid(row=5 + (pos - 1) // 3, column=1 + (pos - 1) % 3, padx=1, pady=1)
            self.buttons[pos] = b
        tk.Label(root, text="").grid(row=8, column=0, pady=2)

    # ---------- game flow ----------
    def reset_board_widgets(self, enable):
        self.board = new_board()
        for b in self.buttons.values():
            b.config(text="", state="normal" if enable else "disabled", bg="gray50")

    def start_game(self):
        self.vs_computer = self.mode.get() == "computer"
        self.p1 = self.letter.get()
        self.p2 = "O" if self.p1 == "X" else "X"
        self.current = self.p1 if self.start_me.get() == "yes" else self.p2
        self.game_over = False
        self.reset_board_widgets(enable=True)
        self.update_status()
        if self.vs_computer and self.current == self.p2:
            self.root.after(400, self.computer_turn)

    def who(self, letter):
        if self.vs_computer:
            return "Player" if letter == self.p1 else "Computer"
        return "Player 1" if letter == self.p1 else "Player 2"

    def update_status(self):
        self.status.config(text=f"{self.who(self.current)}'s turn ({self.current})")

    def on_click(self, pos):
        if self.game_over:
            return
        if self.vs_computer and self.current == self.p2:
            return  # computer is thinking
        if not is_space_free(self.board, pos):
            messagebox.showwarning("Invalid move", "That position is already taken.")
            return
        self.make_move(pos)

    def make_move(self, pos):
        self.board[pos] = self.current
        self.buttons[pos].config(text=self.current, bg="gray70")

        if is_winner(self.board, self.current):
            self.end_game(f"{self.who(self.current)} ({self.current}) wins!")
            return
        if is_draw(self.board):
            self.end_game("It's a draw!")
            return

        self.current = self.p2 if self.current == self.p1 else self.p1
        self.update_status()
        if self.vs_computer and self.current == self.p2:
            self.root.after(400, self.computer_turn)

    def computer_turn(self):
        if self.game_over:
            return
        pos = get_computer_move(self.board, self.p2, self.p1)
        self.make_move(pos)

    def end_game(self, result):
        self.game_over = True
        self.status.config(text=result)
        messagebox.showinfo("Game Over", result)               # display the result
        if messagebox.askyesno("Play again?", "Do you want to start another game?"):
            self.reset_board_widgets(enable=False)
            self.status.config(text="Choose options and press start")
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()