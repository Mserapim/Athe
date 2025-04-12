# -*- coding:utf-8 -*-

import hashlib

from multiprocessing.pool import ThreadPool as Pool

# from multiprocessing import Pool

from django.db import models
from django.conf import settings
from pymongo import MongoClient

from contrib.utils import getLogger

log = getLogger()

CONNECTIONS = {}


def connect(name="default"):
    """Obter conexão com mongodb de arcodo com as configurações de settings.NOSQL_DATABASES"""

    if name not in CONNECTIONS:
        params = settings.NOSQL_DATABASES[name]
        client = MongoClient(
            "mongodb://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(AUTH_DATABASE)s"
            % params
        )
        CONNECTIONS[name] = client
    return CONNECTIONS[name]


def natural_key_by(val):
    """Cria natural key com base no valor passado como parâmetro"""
    return hashlib.md5(str(val).encode()).hexdigest()


class Emperor(object):
    """Multiprocessing executer"""

    def __init__(self, tasks=[], vassals=5, work_tool=None):
        """Construtor de classe.

        Args:
            tasks (iterable): Objeto iterável contendo as tasks a serem executadas.
            vassals (int): Número de vassalos (threads) que executaram as tasks.
            work_tool (callable): Ferramenta (função) que será utilizada pelos vassalos para processar as task.
        """
        self.__tasks = tasks
        self.__labor_camp = Pool(vassals)
        self.work_tool(work_tool)

    def work_tool(self, tool):
        """Informar pós instaciação, a ferramenta (função) que será utilizada pelos vassalos para processar as task.

        Args:
            tool (callable): Ferramenta (função) para processamento das tasks.
        """
        self.__work_tool = tool

    def work(self):
        """Iniciar a execução das tasks."""
        for task in self.__tasks:
            self.__labor_camp.apply_async(self.__work_tool, (task,))

        self.__labor_camp.close()
        self.__labor_camp.join()


class ODMPool(object):
    """Pool de armazenamento de objetos ODM para reaproveitamento de mapeamentos."""

    __instances = {}

    @classmethod
    def create(cls, name, *args, **kwargs):
        """Cria ou retorna uma instância de ODM.
        Caso não exista no pool uma instância com o name informado, uma nova instância é criada e adicionada no pool.
        Caso exista uma instância com o mesmo name no pool, esta é retornada.

        Args:
            name (str): Nome para identificação da instância;
            *args (list): Argumentos posicionais do método de criação do ODM.
            **kwargs (dict): Argumentos nomeados do método de criação do ODM.

            Para mais informações sobre a lista e nome dos argumentos de ODM veja a documentação da classe ODM.
        """
        odm = cls.get(name)
        if not odm:
            odm = ODM(*args, **kwargs)
            cls.add(name, odm)
        return odm

    @classmethod
    def add(cls, name, odm):
        cls.__instances[name] = odm

    @classmethod
    def get(cls, name):
        """Retorna uma instância de ODM caso exista no pool.

        Args:
            name (str): Nome de identificação da instância a ser retornada.
        """
        return cls.__instances.get(name)


class ODM(object):
    """Mapeador Documento Objeto (Object/Document Mapper - ODM).
    Serve para mapear modelos do django objetivando transformar instâncias de modelos em
    documentos MongoDB.
    """

    def __init__(self, exclude=[], fields=[], custom_fields=[], debug=False):
        """Construtor de classe ODM.

        Args:
            exclude (list): Lista com os nomes dos campos do modelo que devem ser ignorados.
                Significa que todos os campos que não estão informados nessa list serão mapeados.

            fields (list): Lista com os nomes dos campos do modelo que devem ser mapeados.
                Significa que somente os campos informados nessa lista serão mapeados.

            custom_fields (list): Lista de campos customizados.
                Campos customizados mapeam propriedades ou métodos do modelo para campos no documento
                utilizando uma lista de dicionários no formato a seguir:

                    {
                        'name': (str)
                        'property': (str)
                        'function': (str)
                        'args': (list)
                        'kwargs': (dict)
                    }

                No modelo acima as chaves do dicionário representam respectivamente:
                * name      => Nome do campo no documento onde os valores das funções ou propriedade serão armazenados;
                * property  => Nome da propriedade a ser executada na instâcia do modelo;
                * function  => Nome do método a ser executado na instância do modelo;
                * args      => Argumentos posicionais para a função
                * kwargs    => Argumento nomeados para a funçã
        """

        self.__debug = debug

        self.__exclude = exclude
        self.__fields = fields
        self.__custom_fields = custom_fields

        self.__relations = {}

        self.__client = None
        self.__db = None
        self.__collection = None

    def fields(self, fields=[]):
        """Método para informar os campos a serem mapeados.

        Args:
            fields (list): Lista com os nomes dos campos do modelo que devem ser mapeados.
        """
        self.__fields = fields
        return self

    def exclude(self, fields=[]):
        """Método para informar os campos que não devem ser mapeados.

        Args:
            fields (list): Lista com os nomes dos campos do modelo que não devem ser mapeados.
        """
        self.__exclude = fields
        return self

    def custom_fields(self, fields):
        """Método para informar a lista de campos customizados que devem ser mapeados.
        Args:
            fields (list): Lista de dicionários com as definições dos custom fields.

        Campos customizados mapeam propriedades ou métodos do modelo para campos no documento
        utilizando uma lista de dicionários no formato a seguir:

            {
                'name': (str)
                'property': (str)
                'function': (str)
                'args': (list)
                'kwargs': (dict)
            }

        No modelo acima as chaves do dicionário representam respectivamente:
        * name      => Nome do campo no documento onde os valores das funções ou propriedade serão armazenados;
        * property  => Nome da propriedade a ser executada na instâcia do modelo;
        * function  => Nome do método a ser executado na instância do modelo;
        * args      => Argumentos posicionais para a função
        * kwargs    => Argumento nomeados para a função

        """
        self.__custom_fields = fields
        return self

    def custom_field(self, **kwargs):
        """Método para adicionar campos custamizados um a um.
        Campos customizados mapeam propriedades ou métodos do modelo para campos no documento

        Args:
            kwargs (dict): Dicionário com as definições dos custom fields.

            Parâmetros nomeados:
            * name      => Nome do campo no documento onde os valores das funções ou propriedade serão armazenados;
            * property  => Nome da propriedade a ser executada na instâcia do modelo;
            * function  => Nome do método a ser executado na instância do modelo;
            * args      => Argumentos posicionais para a função
            * kwargs    => Argumento nomeados para a função

        """
        if kwargs not in self.__custom_fields:
            self.__custom_fields.append(kwargs)

        return self

    def use(self, client):
        """Metódo para informar o client de conexão a ser utilziado.

        Args:
            client (pymongo.mongo_client.MongoClient): Instância do client de conexção.
        """
        self.__client = client
        return self

    def db(self, name):
        """Metódo para informar a base de dados a ser utilziada.

        Args:
            name (str): Nome da base de dados.
        """
        self.__db = self.__client.get_database(name)
        return self

    def to(self, collection_name):
        """Metódo para informar o nome da coleção onde serão salvos os documentos.

        Args:
            collection_name (str): Nome da coleção de documentos.
        """
        self.__collection = collection_name
        return self

    def rel(
        self,
        field,
        only_id=False,
        fields=[],
        exclude=[],
        custom_fields=[],
        query_params={},
        limit=None,
    ):
        """Método para informar os relacionamentos a serem extraídos, o tipo de estratégia do relacionamento
        e definir o conjunto de dados a serem extraídos dos relacionamentos.


        Args:
            field (str): O nome do campo que representa o relacionamento.
            only_id (bool): Tipo de estrategia de relacionamento. Por referência ou objeto embutido.
                Se False, um dicionário com a representação do(s) objeto(s) será usado como referência.
                Se True somente ID será usado como referência e os parâmetros a seguir são desnecessários.
                Default é False.
            fields (list): Lista dos nomes dos campos do(s) de obejto(s) do relacionamento
            exclude (list): Lista dos nomes dos campos do(s) de obejto(s) do relacionamento que devem ser ignorados
            custom_fields (list): Lista de campos customizados a serem feitos
            query_params (dict): Parametros de filtragem do conjunto de objeto(s) de relacionamento
            limit (int): Limite de quantidade de itens do cojunto de objetos

            Exemplo:
                odm_instance.rel(
                    field='entries',
                    only_id=False,
                    query_params={'status': 1, 'active': True, 'deleted': False},
                    limit=100
                )
        """

        self.__relations[field] = {
            "only_id": only_id,
            "fields": fields,
            "exclude": exclude,
            "custom_fields": custom_fields,
            "query_params": query_params,
            "limit": limit,
        }

        return self

    def document(self, model_instance):
        """Cria um docuemnto mongo baseado na definições realizadas em fields, exclude e rel.

        Args:
            model_instance (Model): Instância do modelo de onde será criado o documento.
        """
        juice = ModelJuicer(
            model_instance,
            exclude=self.__exclude,
            fields=self.__fields,
            custom_fields=self.__custom_fields,
            relations=self.__relations,
        )
        return juice.get()

    def save(self, model_instance=None, fake=False):
        """Salva o docuemnto criado a partir de model_instance na base dados Mongo.

        Args:
            model_instance (Model): Instância do modelo de onde será criado o documento.
        """
        document = self.document(model_instance)

        if self.__debug:
            print("%s\n" % self.__collection)
            print("%s\n" % self.__relations)
            print("%s\n" % document)
            print(
                "==========================================================================================="
            )

        if self.__db and not fake:
            collection = self.__db[self.__collection]

            query_criteria = {"_id": document.get("id")}
            if "UID" in document:
                query_criteria = {"UID": document["UID"]}

            # log.info('Checking for update')
            # log.debug(document)
            result = collection.replace_one(query_criteria, document)
            # log.debug('Raw document %s' % result.raw_result)
            # log.info('Update result %s %s' % (result.matched_count, result.modified_count))
            if result.matched_count < 1 and result.modified_count < 1:
                # log.info('Inserting collection')
                result = collection.insert_one(document)

        return document


class ModelJuicer(object):
    """Extrator de atributos, relacionamentos e valores de modelos.
    Serve para criar um dicionário de dados a paritr de um modelo django com base no que é
    informado para extrair e qual extratégia de relacionamento utilizar.
    """

    def __init__(self, model, **kwargs):
        """Construtor de clalsse.

        Args:
            model (django.db.models.Model): Instância do modelo para extração.
            fields (list): Lista de nomes dos atributos que deverão ser extraídos.
                Caso seja omitido, os atributos que serão extraídos são todos os que não constarem em exclude.
            exclude (list): Lista de atruibutos que sevem ser ignorados na extração.
            custom_fields (list): Lista de campos customizados seguindo o modelo de chaves/valor abaixo:
                * name (str): Nome do campo no documento onde os valores das funções ou propriedade serão armazenados;
                * property (str): Nome da propriedade a ser executada na instâcia do modelo;
                * function (str): Nome do método a ser executado na instância do modelo;
                * args (list): Argumentos posicionais para a função;
                * kwargs (dict): Argumento nomeados para a função.

            relations (list): Lista de dicionários que expressa relacionamentos com as chaves a seguir:
                * only_id (bool): Tipo de estrategia de relacionamento. Por referência ou objeto embutido;
                    Se False, um dicionário com a representação do(s) objeto(s) será usado como referência.
                    Se True somente ID será usado como referência e os parâmetros a seguir são desnecessários.
                    Default é False.
                * fields (list): Lista dos nomes dos campos do(s) de obejto(s) do relacionamento;
                * exclude (list): Lista dos nomes dos campos do(s) de obejto(s) do relacionamento que devem ser ignorados;
                * custom_fields (list): Lista de campos customizados a serem feitos
                * query_params (dict): Parametros de filtragem do conjunto de objeto(s) de relacionamento;
                * limit (int): Limite de quantidade de itens do cojunto de objetos.
        """

        self.__model = model
        self.__exclude = kwargs.get("exclude", [])
        self.__fields = kwargs.get("fields", [])
        self.__relations = kwargs.get("relations", {})
        self.__custom_fields = kwargs.get("custom_fields", [])

    def __allowed_fields(self):
        all_field_names = [field.name for field in self.__model._meta.get_fields()]
        field_names = [
            name
            for name in all_field_names
            if not self.__fields or name in self.__fields
        ]
        return [name for name in field_names if name not in self.__exclude]

    def __relation_fields(self):
        def is_relation(x):
            return isinstance(x, models.manager.Manager) or isinstance(x, models.Model)

        return [
            name
            for name in self.__allowed_fields()
            if hasattr(self.__model, name) and is_relation(getattr(self.__model, name))
        ]

    def __value_fields(self):
        return [
            name
            for name in self.__allowed_fields()
            if name not in self.__relation_fields()
        ]

    def __grab(self, name):
        if hasattr(self.__model, name):
            return getattr(self.__model, name)

    def values(self):
        """Retorna um dicionário com atributos e valores extraídos do models, sem os campos de relacionamento"""
        document = {}

        for name in self.__value_fields():
            value = self.__grab(name)
            if name.endswith("id"):
                value = natural_key_by(value)
                if name == "id":
                    document["_id"] = value
            document[name] = value

        return document

    def custom_fields(self):
        """Retorna um dicionário com atributos e valores extraídos do models a partir dos custom fields."""
        custom_fields = {}
        for spec in self.__custom_fields:
            value = None
            name = spec.get("name")
            _property = spec.get("property")

            if _property:
                value = getattr(self.__model, _property)
            else:
                _function = spec.get("function")
                args = spec.get("args", [])
                kwargs = spec.get("kwargs", {})
                value = getattr(self.__model, _function)(*args, **kwargs)
            custom_fields[name] = value
        return custom_fields

    def relations(self):
        """Retorna um dicionário com os relacionamentos do modelo de acordo com os parêmtros informados no construtor."""
        relations = {}

        for name in self.__relation_fields():
            obj = self.__grab(name)

            rel_specs = self.__relations.get(name) or {}
            fields = rel_specs.get("fields") or []
            exclude = rel_specs.get("exclude") or []
            custom_fields = rel_specs.get("custom_fields") or {}

            def juice(x):
                return ModelJuicer(
                    x, fields=fields, exclude=exclude, custom_fields=custom_fields
                ).get(with_relations=False)

            def apply_relation(x):
                return natural_key_by(x.pk) if rel_specs.get("only_id") else juice(x)

            if isinstance(obj, models.Model):
                rel_name = "%s_id" % name if rel_specs.get("only_id") else name
                relations[rel_name] = apply_relation(obj)
            elif rel_specs and isinstance(obj, models.manager.Manager):
                qs = obj.all()

                params = rel_specs.get("query_params")
                limit = rel_specs.get("limit")

                if params:
                    qs = (
                        qs.filter(**params)
                        if isinstance(params, dict)
                        else qs.filter(params)
                    )
                if limit:
                    qs = qs[0:limit]

                relations[name] = [apply_relation(model) for model in qs]

        return relations

    def get(self, with_relations=True):
        """Retorna um dicionario com os valores e relacionamentos extraídos do modelo.

        Args:
            with_relations (bool): Se False, ignora relacionametos. Padrão é True.
        """
        document = self.values()
        document.update(self.custom_fields())
        if with_relations:
            document.update(self.relations())
        return document
