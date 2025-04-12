from contrib.utils import DateUtils, getLogger
from rh.gfp.generators.sicap.protocol import AdministrativeUnitFile
log = getLogger(__name__)

class SicapGenerator(object):

    def __init__(self, **kwargs):
        try:
            self.sicap_helper = SicapHelper(**kwargs)
            self.feedback = kwargs.get('feedback', (lambda progress_message, progress, **kwargs: False))
            self.builder()
        except Exception as err:
            log.exception(err)
            print(err)
            raise err

    @classmethod
    def write_file(cls, text, file_name, mode='w'):
        """
            Método responsável por escrever em file_write.
        """
        try:
            file_write = codecs.open(file_name, mode, 'utf-8')
            file_write.write(text)
            file_write.close()
        except Exception as err:
            log.exception(err)
            raise err

    def generate(self):
    	try:
    		administrative_unit_file_name = '%(directory)s/UnidadeAdministrativa.xml' % self.sicap_helper.sign_file()


    def administrative_unit(self, task=NullTaskSession()):

        log.debug('>>> UNIDADE ADMINISTRATIVA <<<<')
        lines = AdministrativeUnitFile(self.period, task)
        file_path = os.path.join(self.tmp_dir, ' UnidadeAdministrativa.xml')
        self.write_file(self._tags[0] + str(lines) + self._tags[1], file_path mode=self._mode_write)

class SicapHelper(object):
	   """
        Classe suporte para construção de arquivos.
    """

    @classmethod
    def _months_to_unicode(cls, months=[]):
        buf = ''
        for month in months:
            if not buf:
                buf = '%s' % month
            else:
                buf += '-%s' % month
        return buf

    @classmethod
    def _file_name(cls, months=[], year=None):
        return 'mpto-sicapap'

    @classmethod
    def _cache_path(cls):
        cache_path = getattr(settings, 'CACHE', {}).get('sicapap', None)
        if not cache_path:
            cache_path = getattr(settings, 'CACHE_PATH', None)
            if cache_path:
                cache_path = '%s/sicapap' % cache_path
        return cache_path

    @classmethod
    def directory_tmp(cls):
        directory_tmp = SicapUtil._cache_path()
        if not os.path.exists(directory_tmp):
            os.mkdir(directory_tmp)
        return directory_tmp

    def __init__(self, **kwargs):
        self.year = int(kwargs.get('year', None))
        self.months = kwargs.get('months', None)
        if not self.year or not self.months:
            raise Exception('Preencha os parâmetros mês e ano!')
        self.file_name = kwargs.get('file_name', SicapUtil._file_name())
        self.date_start, self.date_end = self.date_start_and_end()
        self.day_start = self.date_start.day
        self.month_start = self.date_start.month
        self.day_end = self.date_end.day
        self.month_end = self.date_end.month
        self.unity_employee = {}  # cpf: count

    def date_start_and_end(self):
        sorted(self.months)
        if len(self.months) > 0:
            month_begin = self.months[0]
            month_end = self.months[len(self.months) - 1]
            day_end = calendar.monthrange(self.year, month_end)[1]
            date_range = NewDateRange(date(self.year, month_begin, 1), date(self.year, month_end, day_end))
        return date_range.first, date_range.last

    @classmethod
    def write_file(cls, text, file_name, mode='w'):
        """
            Método responsável por escrever em file_write.
        """
        try:
            file_write = codecs.open(file_name, mode, 'utf-8')
            file_write.write(text)
            file_write.close()
        except Exception as err:
            log.exception(err)
            raise err

    def sign_file(self):
        return {
            'directory': self.directory_tmp(),
        }
