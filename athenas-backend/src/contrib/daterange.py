# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from contrib.utils import getLogger

log = getLogger(__name__)


class NewDateRange(object):

    INITIAL_DATE = date(1, 1, 1)
    END_DATE = date(9999, 12, 31)
    TYPES_DATE = (date, datetime, type(None))

    class InvalidTypeRanges(Exception):
        pass

    class NotUnionDisjointDateRange(Exception):
        pass

    class NotUnionDisjointRange(Exception):
        pass

    class InvalidTypeRange(Exception):
        pass

    class InvalidDateInRange(Exception):
        def __init__(self, dt_range, *args, **kwargs):
            message = "The date of a range can be date, datetime or None if it is indeterminate! Was found {} ({})!"
            self.message = message.format(dt_range, type(dt_range))
            # Call the base class constructor with the parameters it needs
            # super(InvalidDateInRange, self).__init__()

    class DateEndGreaterThanStart(Exception):
        pass

    def __init__(self, dt1=None, dt2=None, ranges=[], *args, **kwargs):
        # start_date = self.INITIAL_DATE if start_date is None and last else start_date
        # last = self.last if last is None and start_date else last
        self._ranges = []
        if dt1 or dt2:
            ranges = [[dt1, dt2]]
        elif not isinstance(ranges, (list, tuple)):
            raise self.InvalidTypeRanges(
                "Object needs to be started with a list of date range!"
            )

        for drange in ranges:
            self.validate_range_and_normalize(drange)
            self.add_range_to_list(self._ranges, drange)

    def __str__(self):
        value = "["
        for drange in self._ranges:  # sorted(self._ranges, key=lambda x: x[0]):
            if value != "[":
                value += ", "
            value += self.range_to_str(drange)
        value += "] %s day(s)" % self.days
        return value

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other.days == self.days == 0:
            return True
        elif len(self._ranges) == len(other._ranges) and self.days == other.days:
            for x in range(0, len(self._ranges)):
                if self._ranges[x] != other._ranges[x]:
                    return False
                x += 1
            return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        if self.first > other.first:
            return True
        return False

    def __ge__(self, other):
        if self.first >= other.first:
            return True
        return False

    def __lt__(self, other):
        if self.first < other.first:
            return True
        return False

    def __le__(self, other):
        if self.first <= other.first:
            return True
        return False

    def __add__(self, other):
        return self.union(other)

    def __sub__(self, other):
        return self.subtraction(other)

    @classmethod
    def validate_range_and_normalize(
        cls, drange, start_date=date(1, 1, 1), end_date=date(9999, 12, 31)
    ):
        if not (isinstance(drange, (list, tuple)) and len(drange) == 2):
            raise cls.InvalidTypeRange(
                "A period must be started with two dates or one of the dates being None, if not determined!"
            )

        drange[0] = start_date if drange[0] is None else drange[0]
        drange[1] = end_date if drange[1] is None else drange[1]
        drange[0] = drange[0].date() if isinstance(drange[0], datetime) else drange[0]
        drange[1] = drange[1].date() if isinstance(drange[1], datetime) else drange[1]

        if not (
            isinstance(drange[0], cls.TYPES_DATE)
            and isinstance(drange[1], cls.TYPES_DATE)
        ):
            raise cls.InvalidDateInRange(drange)
        elif drange[0] > drange[1]:
            raise cls.DateEndGreaterThanStart(
                "Start date must be earlier than or equal to end date!"
            )

    @classmethod
    def range_to_str(cls, drange):
        return "%s ... %s (%s)" % (drange[0], drange[1], cls.range_days(drange))

    @classmethod
    def range_from_month(cls, year, month):
        dt_last = calendar.monthrange(year, month)
        return [date(year, month, 1), date(year, month, dt_last[1])]

    @classmethod
    def range_days(cls, drange):
        if not drange:
            return 0
        return (drange[1] - drange[0]).days + 1

    @classmethod
    def range_business_days(
        cls, drange, start_date=date(1, 1, 1), end_date=date(9999, 12, 31)
    ):
        days = 0
        if drange[0] == start_date or drange[1] == end_date:
            days = 9999999
        elif drange[0] and drange[1]:
            month = drange[0].month
            year = drange[0].year
            dr_month = cls.range_from_month(year, month)
            dr_month_days = cls.range_days(dr_month)
            dr_intersect = cls.range_intersect(dr_month, drange)
            dr_intersect_days = cls.range_days(dr_intersect)
            days = 0
            while dr_intersect_days > 0:
                if dr_intersect == dr_month:
                    days += 30
                else:
                    dr_intersect_days = cls.range_days(dr_intersect)
                    if dr_intersect[1] == dr_month[1]:
                        days += dr_intersect_days + (30 - dr_month_days)
                    else:
                        days += dr_intersect_days
                month += 1
                if month > 12:
                    year += 1
                    month = 1
                dr_month = cls.range_from_month(year, month)
                dr_month_days = cls.range_days(dr_month)
                dr_intersect = cls.range_intersect(dr_month, drange)
                dr_intersect_days = cls.range_days(dr_intersect)

        return days

    @classmethod
    def range_work_days(
        cls, drange, start_date=date(1, 1, 1), end_date=date(9999, 12, 31)
    ):
        days = 0
        if drange[0] == start_date or drange[1] == end_date:
            days = 9999999
        elif drange[0] and drange[1]:
            d = drange[0]
            while d <= drange[1]:
                if d.isoweekday() not in (6, 7):  # 7: DOMINGO, 6: SABADO
                    days += 1
                d = d + relativedelta(days=1)

        return days

    @classmethod
    def range_intersect(cls, dr1, dr2):
        """Realiza interseção de outro DateRange com este.

        :param other: DateRange a realizar interseção.

        :returns: DateRange resultante da interseção.
        """
        if cls.range_days(dr1) == 0 or cls.range_days(dr2) == 0:
            return []
        drs = sorted([dr1, dr2])
        if drs[1][0] > drs[0][1]:
            return []
        di = drs[0][0] if drs[0][0] >= drs[1][0] else drs[1][0]
        df = drs[0][1] if drs[0][1] <= drs[1][1] else drs[1][1]
        return [di, df]

    @classmethod
    def range_union(cls, dr1, dr2):
        """Realiza união de outro DateRange com este.

        :param other: DateRange a realizar união.

        :returns: DateRange resultante da união.
        """
        if cls.range_days(dr2) == 0:
            return (dr1[0], dr1[1])
        elif cls.range_days(dr1) == 0:
            return (dr2[0], dr2[1])

        drs = sorted([dr1, dr2])
        inter = cls.range_intersect(dr1, dr2)
        if cls.range_days(inter) == 0 and drs[1][0] > (
            drs[0][1] + relativedelta(days=1)
        ):
            return drs
        di = drs[0][0] if drs[0][0] <= drs[1][0] else drs[1][0]
        df = drs[0][1] if drs[0][1] >= drs[1][1] else drs[1][1]
        return [(di, df)]

    @classmethod
    def range_subtraction(cls, dr1, dr2):
        d_inter = cls.range_intersect(dr1, dr2)
        if cls.range_days(dr1) == 0 or d_inter == dr1:
            return []
        elif cls.range_days(dr2) == 0 or cls.range_days(d_inter) == 0:
            return [[dr1[0], dr1[1]]]
        elif d_inter == dr2:
            # TODO Caso em que dr2 esta dentro de dr1 e por isso dr1 - dr2 daria varios DateRanges
            drs = []
            if dr1[0] != dr2[0]:
                drs.append([dr1[0], dr2[0] - relativedelta(days=1)])
            if dr1[1] != dr2[1]:
                drs.append([dr2[1] + relativedelta(days=1), dr1[1]])
            return drs
        elif dr1[0] < dr2[0]:
            return [[dr1[0], dr2[0] - relativedelta(days=1)]]
        elif dr1[1] > dr2[1]:
            return [[dr2[1] + relativedelta(days=1), dr1[1]]]
        return []

    @classmethod
    def merge_ranges_of_date(cls, ranges, start=1, sorted_range=True):
        if not sorted_range:
            ranges = sorted(ranges, key=lambda d: d[0])
        x = start
        while x < len(ranges):
            uranges = cls.range_union(ranges[x - 1], ranges[x])
            if len(uranges) == 1:
                ranges[x - 1][0] = uranges[0][0]
                ranges[x - 1][1] = uranges[0][1]
                # ranges_to_pop.append(drange)
                ranges.pop(x)
            else:
                x += 1
        return ranges

    @classmethod
    def consolidate_ranges_of_date(cls, ranges):
        ranges = sorted(ranges, key=lambda x: x[1])
        cons_ranges = [ranges[0]]
        for i in range(1, len(ranges)):
            urange = NewDateRange.range_union(
                cons_ranges[len(cons_ranges) - 1], ranges[i]
            )
            if len(urange) == 1:
                cons_ranges[len(cons_ranges) - 1] = urange[0]
            else:
                cons_ranges.append(urange[1])

        return cons_ranges

    @classmethod
    def add_range_to_list(cls, ranges, drange, sorted_range=True):
        cls.validate_range_and_normalize(drange)
        if not sorted_range:
            ranges = sorted(ranges, key=lambda d: d[0])
        x = 0
        while x < len(ranges) and ranges[x][0] < drange[0]:
            x += 1
        ranges.insert(x, drange)
        cls.merge_ranges_of_date(ranges, start=max(x, 1))
        return ranges

    @classmethod
    def range_toordinals(cls, drange):
        if not drange:
            return (0, 0)
        return (drange[0].toordinal(), drange[1].toordinal())

    @classmethod
    def range_fromordinals(cls, obj):
        if obj[0] == 0 and obj[1] == 0:
            return []
        return [date.fromordinal(obj[0]), date.fromordinal(obj[1])]

    @property
    def first(self):
        if self._ranges:
            return self._ranges[0][0]
        return None

    @property
    def start_date(self):
        return self.first

    @property
    def last(self):
        if self._ranges:
            return self._ranges[-1][1]
        return None

    @property
    def end_date(self):
        return self.last

    @property
    def days(self):
        days = 0
        for drange in self._ranges:
            days += self.range_days(drange)
        return days

    @property
    def business_days(self):
        days = 0
        for drange in self._ranges:
            days += self.range_business_days(drange)
        return days

    @property
    def work_days(self):
        days = 0
        for dt in self.iter():
            if dt.isoweekday() not in (6, 7):  # 7: DOMINGO, 6: SABADO
                days += 1

        return days

    def copy(self):
        return self.__class__(ranges=self._ranges[:])

    def add_range(self, dt1, dt2):
        drange = [dt1, dt2]
        self.validate_range_and_normalize(drange)
        self.add_range_to_list(self._ranges, drange)

    @staticmethod
    def from_month(year, month):
        """Instancia um NewDateRange a partir de um periodo passado (ano, mes)

        Arguments:
            year {integer} -- Ano do range
            month {integer} -- Mes do range

        Returns:
            [type] -- [description]
        """
        dt_last = calendar.monthrange(year, month)
        return NewDateRange(date(year, month, 1), date(year, month, dt_last[1]))

    @staticmethod
    def from_year(year):
        """Instancia um NewDateRange a partir de um ano passado

        Arguments:
            year {integer} -- Ano do range
            month {integer} -- Mes do range

        Returns:
            [type] -- [description]
        """
        return NewDateRange(date(year, 1, 1), date(year, 12, 31))

    def add_from_month(self, year, month):
        """Adiciona um Range ao objeto atraves de um periodo passado (ano, mes)

        Arguments:
            year {integer} -- Ano do Range
            month {integer} -- Mes do Range
        """
        last_date = calendar.monthrange(year, month)
        self.add_range(date(year, month, 1), date(year, month, last_date[1]))

    def union(self, other):
        """Faz a operacao de union de 2 date ranges

        Arguments:
            other {NewDateRange} -- Um DateRange que se deseja fazer o union com o atual

        Raises:
            Exception: [description]
            Exception: [description]

        Returns:
            NewDateRange -- Result of union
        """
        if not isinstance(other, self.__class__):
            raise Exception(
                "Invalid parameter %s. Must be NewDateRange" % other.__class__.__name__
            )
        new_range = NewDateRange(ranges=self._ranges[:])
        other_ranges = other._ranges[:]
        for dr in other_ranges:
            new_range.add_range(*dr)
        return new_range

    def intersect(self, other):
        if not isinstance(other, self.__class__):
            raise Exception(
                "Invalid parameter %s. Must be NewDateRange" % other.__class__.__name__
            )
        ranges = []
        for dr2 in other._ranges:
            for dr1 in self._ranges:
                if dr2[0] > dr1[1] or dr2[1] < dr1[0]:
                    continue
                ranges.append(self.range_intersect(dr1, dr2))
        return NewDateRange(ranges=ranges)

    def subtraction(self, other):
        if not isinstance(other, self.__class__):
            raise Exception(
                "Invalid parameter %s. Must be NewDateRange" % other.__class__.__name__
            )
        ranges = self._ranges[:]
        # new_range = NewDateRange()
        for dr2 in other._ranges:
            x = 0
            while x < len(ranges):
                if dr2[0] > ranges[x][1] or dr2[1] < ranges[x][0]:
                    x += 1
                    continue
                drs = self.range_subtraction(ranges[x], dr2)
                ranges.pop(x)
                y = len(drs) - 1
                while y >= 0:
                    ranges.insert(x, drs[y])
                    y -= 1
                x = 0
        return NewDateRange(ranges=ranges)

    def contains(self, other):
        """Verifica se outro DateRange está contido neste.

        :param other: DateRange que se quer descobrir se está contido no self(DateRange).

        :returns: Booleano.
        """
        intersect = self.intersect(other)
        return other == intersect

    def toordinals(self):
        ordinals = []
        for drange in self._ranges:
            ordinals.append(self.range_toordinals(drange))

        return ordinals

    @classmethod
    def fromordinals(cls, objs):
        ranges = []
        for obj in objs:
            ranges.append(cls.range_fromordinals(obj))

        return cls(ranges=ranges)

    def to_list(self):
        list_date = []
        for drange in self._ranges:
            dt = drange[0]
            while drange[0] <= dt <= drange[1]:
                list_date.append(dt)
                dt += relativedelta(days=1)
        return list_date

    def iter(self):
        """Cria uma iteração ordenada com todas as datas do DateRange. OBS.: Apenas para DateRange FINITO.

        :returns: Iterador.
        """
        for dt in self.to_list():
            yield dt

    def in_range(self, dt):
        for drange in self._ranges:
            if drange[0] <= dt <= drange[1]:
                return True
        return False

    def ranges(self):
        """
        :returns: Lista ordenada de DateRange
        """
        return self._ranges

    def iter_ranges(self):
        """Cria uma iteração ordenada com todos os DateRanges.

        :returns: Iterador
        """
        for drange in self._ranges:
            yield drange

    @staticmethod
    def next_day_weekend(dt=None):
        dt = datetime.now() if not dt else dt
        if dt.isoweekday() not in (6, 7):
            return dt
        else:
            while dt.isoweekday() in (6, 7):
                dt = dt + relativedelta(days=1)
            return dt

    @staticmethod
    def day_weekend(dt=None):
        """
        Este método retorna se a dt informada é do fim de semana.
        """
        # sabado = 5
        # domingo = 6
        dt = datetime.now() if not dt else dt
        return dt.isoweekday() in (6, 7)

    @property
    def is_continuous(self):
        return len(self.ranges()) == 1

    @classmethod
    def separar_datas_ano_distintos(cls, dt_inicio, dt_fim):
        MES_FINAL = 12
        MES_INICIAL = 1
        dt_fim_ano = datetime(dt_inicio.year, MES_FINAL, 31).date()
        dt_inicio_ano = datetime(dt_fim.year, MES_INICIAL, 1).date()

        if dt_fim > dt_fim_ano:
            return [
                {
                    "dt_inicio": dt_inicio,
                    "dt_fim": dt_fim_ano,
                    "dias": NewDateRange(dt_inicio, dt_fim_ano).days,
                },
                {
                    "dt_inicio": dt_inicio_ano,
                    "dt_fim": dt_fim,
                    "dias": NewDateRange(dt_inicio_ano, dt_fim).days,
                },
            ]
        dias = NewDateRange(dt_inicio, dt_fim).days
        return [{"dt_inicio": dt_inicio, "dt_fim": dt_fim, "dias": dias}]
