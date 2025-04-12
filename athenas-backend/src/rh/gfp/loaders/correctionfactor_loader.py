# from xlrd import open_workbook, xldate_as_datetime

# from ged.models import Arquivo as File
# from rh.gfp.models import CorrectionFactor


# class LoaderCorrectionFraction:

#     def __init__(self, *args, **kwargs):
#         self.startyear = kwargs.get('startyear', None)
#         self.paid_year = kwargs.get('year', None)
#         self.paid_month = kwargs.get('month', None)
#         try:
#             self.correctionfile = File.objects.filter(pk=kwargs.get('correctionfile', None)).last()
#         except Exception as error:
#             print('Arquivo não encontrado!')

#     def load_from_xls(self):
#         wb = open_workbook(self.correctionfile.absolute_path)
#         sheet = wb.sheet_by_index(0)
#         factors = {}

#         for row in sheet.get_rows():
#             def xldate_to_date(value): return xldate_as_datetime(row[0].value, wb.datemode).date()
#             if row[0].value and xldate_to_date(row[0]).year >= self.startyear:
#                 ref_date = xldate_to_date(row[0])
#                 value = row[1].value
#                 print(f'{ref_date.month:02d}/{ref_date.year:04d}: {value}', end='')
#                 cf, created = CorrectionFactor.objects.update_or_create(
#                     identifier='JEBRN',
#                     ref_payment_year=self.paid_year,
#                     ref_payment_month=self.paid_month,
#                     ref_difference_year=ref_date.year,
#                     ref_difference_month=ref_date.month,
#                     defaults={'factor': value}
#                 )
#                 print(' U' if not created and 'factor' in cf.diff else ' C')
#                 factors[(ref_date.month, ref_date.year)] = value

#         return factors
