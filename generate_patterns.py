#!/usr/bin/env python3
"""
generate_patterns.py — regenerate all bundled pattern files.
Run: python3 generate_patterns.py
"""

import math
import os

ROWS = 7
COLS = 52

def make_grid():
    return [[' '] * COLS for _ in range(ROWS)]

def grid_to_str(grid):
    return '\n'.join(''.join(row).rstrip() for row in grid) + '\n'

def make_heart():
    g = make_grid()
    heart = [" ##   ## ","#########","#########"," ####### ","  #####  ","   ###   ","    #    "]
    left = (COLS - len(heart[0])) // 2
    for r, row_pat in enumerate(heart):
        for i, ch in enumerate(row_pat):
            c = left + i
            if 0 <= c < COLS: g[r][c] = ch
    return grid_to_str(g)

def make_gradient():
    row = '.' * 13 + 'o' * 13 + 'O' * 13 + '#' * 13
    return '\n'.join([row] * ROWS) + '\n'

def make_wave():
    g = make_grid()
    shading = ['.', 'o', 'O', '#']
    for c in range(COLS):
        peak = round(2 + 2 * math.sin(2 * math.pi * c / 16))
        peak = max(0, min(ROWS - 1, peak))
        g[peak][c] = '#'
        for r in range(peak + 1, ROWS):
            g[r][c] = shading[min(r - peak - 1, len(shading)-1)]
    return grid_to_str(g)

def make_pacman():
    g = make_grid()
    left = 22
    body = ["  ####  "," ###### ","########","####    ","####    ","########","  ####  "]
    for r, row_pat in enumerate(body):
        for i, ch in enumerate(row_pat):
            c = left + i
            if 0 <= c < COLS and ch != ' ': g[r][c] = ch
    for col, intensity in [(34,'#'),(38,'O'),(42,'o'),(46,'.')]:
        if col < COLS: g[3][col] = intensity
    ghost_left = 9
    ghost_rows = [" OOO ","OOOOO","O.O.O","OOOOO","O O O"]
    for i, row_pat in enumerate(ghost_rows):
        r = 1 + i
        for j, ch in enumerate(row_pat):
            c = ghost_left + j
            if 0 <= c < COLS and ch != ' ': g[r][c] = ch
    return grid_to_str(g)

def make_cloaked():
    g = make_grid()
    for c in range(18):
        g[0][c] = '#' if (c%5) not in (2,4) else 'O'
        g[1][c] = '#'; g[2][c] = 'O' if c%2==0 else '#'
        if c%4==0: g[3][c]='#'; g[4][c]='#'
        g[5][c]='o'; g[6][c]='O'
    for c in range(18,22):
        g[0][c]='O' if c<20 else ' '; g[1][c]='O' if c<20 else ' '
        g[2][c]='#' if c<19 else ('O' if c<21 else 'o')
        g[3][c]=g[4][c]=g[5][c]='o'; g[6][c]='O'
    for c in range(22,34):
        g[2][c]='.'; g[3][c]='.'; g[4][c]='o'; g[5][c]='o'; g[6][c]='O'
    for c in range(34,38):
        g[1][c]='O' if c>=36 else ' '
        g[2][c]='o' if c==34 else ('O' if c>=36 else 'o')
        g[3][c]=g[4][c]=g[5][c]='o'; g[6][c]='O'
    for c in range(38,52):
        i=c-38
        g[0][c]='#' if (i%5) not in (1,3) else 'O'
        g[1][c]='#'; g[2][c]='O' if i%2==0 else '#'
        if i%4==0: g[3][c]='#'; g[4][c]='#'
        g[5][c]='o'; g[6][c]='O'
    fig=27
    g[0][fig]='O'; g[1][fig]='#'; g[1][fig-1]='O'; g[1][fig+1]='O'
    for c in range(fig-2,fig+3): g[2][c]='#'
    for c in range(fig-1,fig+2): g[3][c]='#'
    g[4][fig-1]=g[4][fig]=g[4][fig+1]='O'; g[5][fig]='O'
    return grid_to_str(g)

if __name__ == "__main__":
    os.makedirs('patterns', exist_ok=True)
    patterns = {'heart':make_heart,'gradient':make_gradient,'wave':make_wave,'pacman':make_pacman,'cloaked':make_cloaked}
    for name, fn in patterns.items():
        path = f'patterns/{name}.txt'
        with open(path,'w') as f: f.write(fn())
        print(f'wrote {path}')
