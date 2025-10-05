"""
Meridyenlerdeki buglar yüzünden bazı eyaletlerin koordinatları için fixler
"""
import math
from typing import Dict, List
import pandas as pd

limit_0 = 1e-12 # 0.000000000000000...1

"""
long [180,-180] arası kıstır]
"""
def wrap(long : float) -> float:
    if long > 180.0:
        return long - 360.0
    if long < -180.0:
        return long + 360.0
    return long
 
"""
meridyen ortasını bulmak için fonksiyon
"""
def mid_lon(lon_w : float, lon_e : float) -> float:
    a = math.radians(lon_w)
    b = math.radians(lon_e)
    x = math.cos(a) + math.cos(b) 
    y = math.sin(a) + math.sin(b)
    if abs(x) < limit_0 and abs(y) < limit_0:
        # mutlak değerler arasındaki ilişki bu sa (fark yok) kıstırmamız gerekir
        return wrap(lon_w)
    return wrap(math.degrees(math.atan2(y, x))) # yoksa arctanjant al, sonra yeniden dereceye çevir, kıstır
