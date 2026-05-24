import curses
import time
import random
import math
import json
import os


PADDLE_SIZE = 5
BALL_SPEED = 0.4
WIN_SCORE = 5
SPEED_INCREASE = 1.05
MAX_BOUNCE = 0.8

SCORES_FILE = "scores.json"


def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as file:
            return json.load(file)
    return {}


def save_winner(name):
    scores = load_scores()

    if name in scores:
        scores[name] += 1
    else:
        scores[name] = 1

    with open(SCORES_FILE, "w") as file:
        json.dump(scores, file, indent=4)


def reset_ball(w, h):
    angle = random.uniform(-0.5, 0.5)

    direction = random.choice([-1, 1])

    dx = math.cos(angle) * BALL_SPEED * direction
    dy = math.sin(angle) * BALL_SPEED

    return w // 2, h // 2, dx, dy


def draw(stdscr, left_y, right_y, ball_x, ball_y, score_l, score_r):
    stdscr.clear()

    h, w = stdscr.getmaxyx()

    stdscr.border()

    stdscr.addstr(0, w // 2 - 3, f"{score_l}:{score_r}")

    for i in range(PADDLE_SIZE):
        stdscr.addch(int(left_y) + i, 2, '|')

    for i in range(PADDLE_SIZE):
        stdscr.addch(int(right_y) + i, w - 3, '|')

    stdscr.addch(int(ball_y), int(ball_x), 'O')

    controls = "W/S = Left   UP/DOWN = Right   P = Pause   L = Leaderboard   Q = Quit"

    stdscr.addstr(h - 1, 2, controls[:w - 4])

    stdscr.refresh()


def game(stdscr): 
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    h, w = stdscr.getmaxyx()

    left_y = h // 2
    right_y = h // 2

    ball_x, ball_y, ball_dx, ball_dy = reset_ball(w, h)

    score_l = 0
    score_r = 0

    while True:
        key = stdscr.getch()

        if key == ord('p'):
            stdscr.addstr(h // 2, w // 2 - 5, "PAUSED")
            stdscr.refresh()

            while True:
                pause_key = stdscr.getch()

                if pause_key == ord('p'):
                    break

                time.sleep(0.1)

        if key == ord('l'):
            scores = load_scores()

            stdscr.clear()
            stdscr.border()

            stdscr.addstr(1, 2, "Leaderboard")

            row = 3

            if scores:
                for name, wins in scores.items():
                    stdscr.addstr(row, 2, f"{name}: {wins} wins")
                    row += 1
            else:
                stdscr.addstr(row, 2, "No scores yet")

            stdscr.addstr(h - 2, 2, "Press any key to return")

            stdscr.refresh()

            stdscr.nodelay(False)
            stdscr.getch()
            stdscr.nodelay(True)

        if key == ord('q'):
            break

        if key == ord('w'):
            left_y -= 1

        if key == ord('s'):
            left_y += 1

        if key == curses.KEY_UP:
            right_y -= 1

        if key == curses.KEY_DOWN:
            right_y += 1

        left_y = max(1, min(h - PADDLE_SIZE - 1, left_y))
        right_y = max(1, min(h - PADDLE_SIZE - 1, right_y))

        ball_x += ball_dx
        ball_y += ball_dy

        if ball_y <= 1 or ball_y >= h - 2:
            ball_dy *= -1

        if int(ball_x) == 3 and ball_dx < 0:
            if left_y <= ball_y <= left_y + PADDLE_SIZE:

                hit_pos = (ball_y - (left_y + PADDLE_SIZE / 2)) / (PADDLE_SIZE / 2)

                hit_pos = max(-MAX_BOUNCE, min(MAX_BOUNCE, hit_pos))

                speed = math.sqrt(ball_dx**2 + ball_dy**2) * SPEED_INCREASE

                ball_dx = abs(speed * math.cos(hit_pos))
                ball_dy = speed * math.sin(hit_pos)

        if int(ball_x) == w - 4 and ball_dx > 0:
            if right_y <= ball_y <= right_y + PADDLE_SIZE:

                hit_pos = (ball_y - (right_y + PADDLE_SIZE / 2)) / (PADDLE_SIZE / 2)

                hit_pos = max(-MAX_BOUNCE, min(MAX_BOUNCE, hit_pos))

                speed = math.sqrt(ball_dx**2 + ball_dy**2) * SPEED_INCREASE

                ball_dx = -abs(speed * math.cos(hit_pos))
                ball_dy = speed * math.sin(hit_pos)

        if ball_x < 1:
            score_r += 1

            ball_x, ball_y, ball_dx, ball_dy = reset_ball(w, h)

            time.sleep(1)

        if ball_x > w - 2:
            score_l += 1

            ball_x, ball_y, ball_dx, ball_dy = reset_ball(w, h)

            time.sleep(1)

        if score_l >= WIN_SCORE:
            stdscr.clear()
            stdscr.addstr(h // 2, w // 2 - 10, "Left Player Wins!")
            stdscr.refresh()

            save_winner("Left Player")

            time.sleep(3)
            break

        if score_r >= WIN_SCORE:
            stdscr.clear()
            stdscr.addstr(h // 2, w // 2 - 10, "Right Player Wins!")
            stdscr.refresh()

            save_winner("Right Player")

            time.sleep(3)
            break

        draw(stdscr, left_y, right_y, ball_x, ball_y, score_l, score_r)

        time.sleep(0.02)


curses.wrapper(game)