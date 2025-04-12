# -*- coding: utf-8 -*-

from rh.gfp.febrabam import bb
from rh.gfp.febrabam import cef
from rh.gfp.febrabam import real
from rh.gfp.febrabam import hsbc
from rh.gfp.febrabam import itau
from rh.gfp.febrabam import santander
from rh.gfp.febrabam import bradesco

protocols = [bb, cef, real, hsbc, itau, santander, bradesco]


def get_protocol(hid):
    ptl = None

    for p in protocols:
        if p.__hid__ == hid:
            ptl = p
            break

    return ptl
