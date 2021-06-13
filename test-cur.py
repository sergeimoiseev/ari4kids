#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses
from curses.textpad import Textbox, rectangle
from random import randint
import pandas as pd
from datetime import datetime
import os

menu = ['учиться', 'посмотреть журнал', 'выйти']
test_len = 10
df = pd.DataFrame(index=range(test_len), columns=[
        'name',
        'a','b','res','elapsed_time','correct', 'test_res', 'test_len'
    ])
fpath = "c:\\Users\\Sergei\\Dropbox\\ari4kids\\"

def print_menu(stdscr, selected_row_idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    # печать меню с выделением выбранной строки
    for idx, row in enumerate(menu):
        x = w//2 - len(row)//2
        y = h//2 - len(menu)//2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
    stdscr.refresh()


def print_center(stdscr, text):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x = w//2 - len(text)//2
    y = h//2
    stdscr.addstr(y, x, text)
    stdscr.refresh()

def learn_ui(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    a = randint(1,10)
    b = randint(1,4)
    stdscr.addstr(0, 0, "%d + %d = " % (a, b))

    editwin = curses.newwin(1,10, 2,1)
    rectangle(stdscr, 1,0, 1+1+1, 1+10+1)
    stdscr.refresh()
    return a + b, a, b, editwin

def save_results(i,a,b,res, correct, test_res, test_len):
    # df.iloc[i,:]['name']=name
    df.iloc[i,:]['a'] = a
    df.iloc[i,:]['b'] = b
    df.iloc[i,:]['res'] = res
    # df.iloc[i,:]['elapsed_time'] = elapsed_time
    df.iloc[i,:]['correct'] = correct
    df.iloc[i,:]['test_res'] = test_res
    df.iloc[i,:]['test_len'] = test_len

def main(stdscr):
    # turn off cursor blinking
    curses.curs_set(0)

    # color scheme for selected row
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # specify the current selected row
    current_row = 0

    # print the menu
    print_menu(stdscr, current_row)

    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            print_center(stdscr, "Ты решил '{}'".format(menu[current_row]))
            stdscr.getch()
            # if user selected last row, exit the program
            if current_row == len(menu)-1:
                break
            elif menu[current_row] == "учиться":

                test_res = 0
                for i in range(test_len):
                    answ, a, b, editwin = learn_ui(stdscr)

                    box = Textbox(editwin)
                    # Позвольте пользователю редактировать, пока не будет нажата Ctrl-G.
                    box.edit()
                    # Получить результирующее содержимое
                    message = box.gather()
                    num_entered = int(message.split()[0])
                    if answ == num_entered:
                        test_res += 1
                        correct = True
                        print_center(stdscr, "Твой ответ %d. Верно!" % (num_entered))
                    else:
                        correct = False
                        print_center(stdscr, "Твой ответ %d. Ошибся.." % (num_entered))
                    save_results(i,a,b, num_entered, correct, test_res, test_len)
                    stdscr.refresh()
                    stdscr.getch()
                df.to_excel(os.path.join(fpath,
                    "ari4kids_test %s %s.xlsx" % ('curses_test',
                    datetime.now().strftime("%m_%d_%Y %H_%M_%S"))))

        print_menu(stdscr, current_row)


curses.wrapper(main)