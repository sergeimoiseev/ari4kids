#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses

from ui import main


curses.wrapper(main)
