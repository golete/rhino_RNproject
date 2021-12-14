import bisect
#x is the number to round to closes divisor and n is the base integer
def round_to_divisor(x,n):
    a = []
    for i in range(1,n/2+1):
        if n%i == 0:
            a.append(i)

    beg = bisect.bisect_left(a,x)
    lo = a[beg-1]
    hi = a[beg]

    dif_lo = abs(x-lo)
    dif_hi = abs(x-hi)
    if dif_lo <= dif_hi:
        return (lo)
    else:
        return (hi)
