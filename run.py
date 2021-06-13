#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randint
import time
import pandas as pd
from datetime import datetime

test_len = 10

df = pd.DataFrame(index=range(test_len), columns=[
        'name',
        'a','b','res','elapsed_time','correct', 'test_res', 'test_len'
    ])

def save_results(i,name,a,b,res,elapsed_time, correct, test_res, test_len):
    df.iloc[i,:]['name']=name
    df.iloc[i,:]['a'] = a
    df.iloc[i,:]['b'] = b
    df.iloc[i,:]['res'] = res
    df.iloc[i,:]['elapsed_time'] = elapsed_time
    df.iloc[i,:]['correct'] = correct
    df.iloc[i,:]['test_res'] = test_res
    df.iloc[i,:]['test_len'] = test_len
    # print(df)

name = input("Введи свое имя: ")
print("Привет, %s! \nРеши %d примеров на сложение." % (name,test_len))

test_res = 0
for i in range(test_len):
    # a = randint(1,10)
    a = 1
    b = randint(1,10)
    start = time.time()
    res = int(input("%d + %d = " % (a, b)))
    end = time.time()
    elapsed_time = end - start
    if res == a+b:
        print("Верно!")
        test_res += 1
        correct = True
    else:
        print("Попробуй следующий пример.")
        correct = False
    print("Пример %d из %d:" % (i+1, test_len))
    save_results(i,name,a,b,res,elapsed_time, correct, test_res, test_len)
# backup_results
df.to_excel('ari4kids_test_%s.xlsx' % (datetime.now().strftime("%m_%d_%Y, %H_%M_%S")))
if test_res == test_len:
    print("Все примеры решены верно!")
elif test_res > test_len/2:
    print("%d из %d решено верно!" % (test_res,test_len))
else:
    print("Из %d решено %d." % (test_len,test_res))


input("Нажми Enter, чтобы закрыть программу. Пока!")