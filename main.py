from curses_tools import draw_frame, read_controls, get_frame_size
import time
import curses
import asyncio
import random


async def blink(canvas, row, column, symbol='*'):
    initial_start = random.randint(0, 5)
    while True:
        while initial_start > 0:
            await asyncio.sleep(0)
            initial_start -= 1

        for _ in range(0, 20):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)

        for _ in range(0, 3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)

        for _ in range(0, 5):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)

        for _ in range(0, 3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-1, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def calculate_coordinate(coordinate, max_coordinate, direction, size):
    if direction < 0:
        if abs(direction) >= coordinate:
            new_coordinate = 1
        else:
            new_coordinate = coordinate + direction
    else:
        if direction >= max_coordinate - (coordinate + size):
            new_coordinate = max_coordinate - size - 1
        else:
            new_coordinate = coordinate + direction

    return new_coordinate


def get_direction(canvas, row, column, row_size, column_size):
    max_row, max_column = canvas.getmaxyx()
    rows_direction, columns_direction, space_pressed = read_controls(canvas)
    if rows_direction == 0:
        new_row = row
    else:
        new_row = calculate_coordinate(row, max_row, rows_direction, row_size)

    if columns_direction == 0:
        new_column = column
    else:
        new_column = calculate_coordinate(column, max_column, columns_direction, column_size)

    return new_row, new_column


async def animate_spaceship(canvas, start_row, start_column, frame_1, frame_2):
    row, column = start_row, start_column
    row_size, column_size = get_frame_size(frame_1)
    while True:
        row, column = get_direction(canvas, row, column, row_size, column_size)
        draw_frame(canvas, row, column, frame_1)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame_1, True)

        row, column = get_direction(canvas, row, column, row_size, column_size)
        draw_frame(canvas, row, column, frame_2)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame_2, True)


def get_star_coroutines(canvas, stars_number, max_row, max_column):
    star_coroutines = []
    for _ in range(0, stars_number):
        row = random.randint(1, max_row - 2)
        column = random.randint(1, max_column - 2)
        star_symbol = random.choice('+*.:')
        star = blink(canvas, row, column, star_symbol)
        star_coroutines.append(star)

    return star_coroutines


def get_rocket_frames():
    with open('rocket/rocket_frame_1.txt', 'r') as file:
        rocket_frame_1 = file.read()

    with open('rocket/rocket_frame_2.txt', 'r') as file:
        rocket_frame_2 = file.read()

    return rocket_frame_1, rocket_frame_2


def draw(canvas):
    canvas.nodelay(True)
    curses.curs_set(False)
    canvas.border()
    max_row, max_column = canvas.getmaxyx()
    coroutines = get_star_coroutines(canvas, 200, max_row, max_column)
    start_row, start_column = max_row // 2, max_column // 2
    fire_coroutine = fire(canvas, start_row, start_column)
    coroutines.append(fire_coroutine)
    start_column -= 2
    rocket_frame_1, rocket_frame_2 = get_rocket_frames()
    animate_spaceship_coroutine = animate_spaceship(canvas, start_row, start_column, rocket_frame_1, rocket_frame_2)
    coroutines.append(animate_spaceship_coroutine)
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)

        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
