x_start = 0
x_current = 0
x_finish = 10.0
rate = 0.01
cycle = 0.004

current_pos = 0

interval = x_finish/rate

# 1 step = 0.004 or 0.012 ms
# max 1 step = 2000 mm/s
# 1% = 20 mm/s
# 20 mm in 0.004 ms


while round(x_current,2) is not round(x_finish,2):
    x_current += rate
    print(round(x_current, 2))