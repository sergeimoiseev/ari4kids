#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses
from curses.textpad import Textbox, rectangle
from random import randint
import pandas as pd
from datetime import datetime
import os
import time
from platform import uname, system

def in_wsl() -> bool:
    """
    WSL is thought to be the only common Linux kernel with Microsoft in the name, per Microsoft:
    https://github.com/microsoft/WSL/issues/4071#issuecomment-496715404
    """
    return 'WSL' in uname().release


menu = ['учиться', 'посмотреть журнал', 'выйти']
test_len = 10
max_think_time = 5
df = pd.DataFrame(index=range(test_len), columns=[
        'name',
        'a','b','user_input','elapsed_time','correct', 'test_score', 'test_len', 'max_think_time', 'solved_in_mind'
    ])

# TODO: при первом запуске запрашивать путь до папки, затем хранить его в неверсионируемом файле
if system() == 'Linux':
    print("This code is running on a Linux system.")
    fpath = os.path.join("~","Dropbox","ari4kids")
    # raise(os.error)
else:
    print(f"This code is running on a {system()} system, not Linux.")
    if in_wsl():
        # не работает - в wsl возвращате False
        fpath = os.path.join("mnt","c","Users","User","Dropbox","ari4kids")
    else:
        fpath = os.path.join("c:",os.sep,"Users","User","Dropbox","ari4kids")

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
    if in_wsl():
        stdscr.addstr(0, 0, "Сейчас я работаю в WSL!")
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
    stdscr.addstr(0, 0, "%d * %d = " % (a, b))

    editwin = curses.newwin(1,10, 2,1)
    rectangle(stdscr, 1,0, 1+1+1, 1+10+1)
    stdscr.refresh()
    return a * b, a, b, editwin

def save_results(i,name,a,b,user_input,elapsed_time, correct, test_score, test_len):
    df.iloc[i,:]['name']=name
    df.iloc[i,:]['a'] = a
    df.iloc[i,:]['b'] = b
    df.iloc[i,:]['user_input'] = user_input
    df.iloc[i,:]['elapsed_time'] = elapsed_time
    df.iloc[i,:]['correct'] = correct
    df.iloc[i,:]['test_score'] = test_score
    df.iloc[i,:]['test_len'] = test_len
    df.iloc[i,:]['max_think_time'] = max_think_time
    df.iloc[i,:]['solved_in_mind'] = max_think_time > elapsed_time
    

def main(stdscr):
    # turn off cursor blinking
    curses.curs_set(0)

    # color scheme for selected row
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # specify the current selected row
    current_row = 0

    # Просим представиться
    stdscr.clear()
    stdscr.addstr(0, 0, "Я - Арифметик! А как тебя зовут?")
    editwin = curses.newwin(1,30, 2,1)
    rectangle(stdscr, 1,0, 1+1+1, 1+30+1)
    stdscr.refresh()
    name_box = Textbox(editwin)
    # Позвольте пользователю редактировать, пока не будет нажата Ctrl-G.
    name_box.edit()
    # Получить результирующее содержимое
    name = name_box.gather().strip()
    print_center(stdscr, "Привет, {}! Нажми любую клавишу, чтобы продолжить.".format(name))
    stdscr.getch()
    stdscr.refresh()

    # print the menu
    print_menu(stdscr, current_row)

    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            
            # if user selected last row, exit the program
            if current_row == len(menu)-1:
                break
            elif menu[current_row] == "учиться":

                test_score = 0
                for i in range(test_len):

                    answ, a, b, editwin = learn_ui(stdscr)

                    box = Textbox(editwin)
                    # засекаем время
                    start = time.time()
                    # Позвольте пользователю редактировать, пока не будет нажата Ctrl-G.
                    box.edit()
                    # Получить результирующее содержимое
                    message = box.gather()
                    elapsed_time = time.time() - start
                    num_entered = int(message.split()[0])
                    if answ == num_entered:
                        test_score += 1
                        correct = True
                        # print_center(stdscr, "Твой ответ %d. Верно!" % (num_entered))
                    else:
                        correct = False
                        # print_center(stdscr, "Твой ответ %d. Ошибся.." % (num_entered))
                    save_results(i,name,a,b,num_entered,elapsed_time, correct, test_score, test_len, )
                    # stdscr.refresh()
                    # stdscr.getch()
                df.to_excel(os.path.join(fpath,
                    "ari4kids_test %s %s.xlsx" % (name,
                    datetime.now().strftime("%m_%d_%Y %H_%M_%S"))))
            else:
                print_center(stdscr, 
                    "Ты выбрал {}, но это пока не возможно. Нажми любую клавишу, чтобы вернуться в меню.".format(menu[current_row]))
                stdscr.getch()
        print_menu(stdscr, current_row)


curses.wrapper(main)