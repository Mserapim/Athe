import decimal
import pprint

_d = decimal.Decimal

decimal.getcontext().rounding = decimal.ROUND_DOWN

table = {
    _d("1045"): [_d(0), _d("0.075"), _d(0)],
    _d("2089.60"): [_d("1045"), _d("0.09"), _d("15.68")],
    _d("3134.40"): [_d("2089.60"), _d("0.12"), _d("78.3720")],
    _d("6101.06"): [_d("3134.40"), _d("0.14"), _d("141.0664")],
}

# B * P - R = I


def inss(base):
    total1 = _d(0)
    for vrange in table:
        total1 += round((min(base, vrange) - table[vrange][0]) * table[vrange][1], 2)
        if base <= vrange:
            break
    partial2 = min(base, vrange) * table[vrange][1]
    total2 = round(partial2 - table[vrange][2], 2)

    return tuple(table[vrange]) + (partial2 - total1, base, total1, total2, vrange)


def test_inss(max_v, internal=False):
    for x in range(1, max_v):
        base = _d(x) / 100
        res = inss(base)
        if res[5] != res[6]:
            print(res, flush=True)
            if not internal:
                table[res[7]][2] = res[3]
                if not test_inss(x, True):
                    print(res, flush=True)
                    return False
            else:
                return False
        else:
            print(base, end="\r", flush=True)
    return True


test_inss(1000000)
pprint.pprint(table)
