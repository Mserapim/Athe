# -.- coding: utf-8 -.-
from django.core.management.base import BaseCommand
from engine import models as engine_models
from engine.models import Application
from engine.models import Controller
from glib.option import make_option


class Command(BaseCommand):
    verbose = "False"
    help = "Comando instalador."

    option_list = BaseCommand.option_list + (
        make_option(
            "--cviews=True", nargs=1, dest="create_views", help="Cria arquivo de views."
        ),
        make_option(
            "--cmenu=True",
            nargs=1,
            dest="create_menu",
            help="Cria menu e instala aplicações em cada menu.",
        ),
        make_option(
            "--file_views",
            nargs=1,
            dest="file_views",
            help="Nome do arquivo de views que será criado.",
        ),
        make_option(
            "--verbose", nargs=1, dest="verbose", help="Exibe todas as saídas."
        ),
    )

    def handle(self, *args, **options):
        try:
            new_args = []
            if options["create_views"]:
                new_args.append(options["create_views"])
            else:
                new_args.append("False")
            if options["create_menu"]:
                new_args.append(options["create_menu"])
            else:
                new_args.append("False")
            if options["file_views"]:
                new_args.append(options["file_views"])
            else:
                new_args.append("views.py")
            if options["verbose"]:
                self.verbose = options["verbose"]
            else:
                self.verbose = "False"
            self.install_applications(new_args[0], new_args[1], new_args[2])
        except:
            raise

    def insert_application(self, *args):
        """
        args[0] => Label
        args[1] => menu pai
        return => retorna o id da aplicação inserida, ou None
        """
        label = args[0]

        try:
            menu_pai = args[1]
            app_father = Application.objects.get(pk=menu_pai)
        except:
            app_father = None
            menu_pai = None
        try:
            engine_application = Application()
            engine_application.title = label
            engine_application.father = app_father
            engine_application.active = True
            engine_application.save()
            return str(engine_application.pk)
        except:
            raise
            return None

    def procura_filho(self, *args):
        """
        args[0] => lista
        """
        menu = args[0]
        value = args[1]
        try:
            if isinstance(menu, list):
                cont = 0
                encontrado = False
                for m in menu:
                    if isinstance(m, list):
                        valor = self.procura_filho(m, value)
                        if valor:
                            return valor
                    else:
                        if cont == 1:
                            if m == value:
                                encontrado = True
                        if cont == 2 and encontrado:
                            return m
                        cont = cont + 1
        except:
            raise

    def procura_pai(self, *args):
        """
        args[0] => lista
        """
        menu = args[0]
        value = args[1]
        try:
            for m in menu:
                for mm in m:
                    if mm == value:
                        return m
            return None
        except:
            raise

    def busca_application_id(self, *args):
        """
        args[0] => menu
        args[1] => application
        args[2] => node_menu que deverá ser encontrado
        """
        menu_pai = self.procura_pai(args[0], args[1])
        if menu_pai:
            return self.procura_filho(menu_pai, args[2])
        else:
            return None

    def lista(self, *args):
        """
        args[0] => lista
        args[1] => id do menu pai
        return => retorna o menu completo
        """
        value = args[0]
        try:
            menu_pai = args[1]
        except:
            menu_pai = None
        sub = []
        id = None
        try:
            if isinstance(value, list):
                cont = 0
                for m in value:
                    if isinstance(m, list):
                        sub.append(self.lista(m, id))
                    else:
                        if cont == 0:
                            label = m
                        if cont == 2:
                            id = self.insert_application(label, menu_pai)
                            sub.append(id)
                        else:
                            sub.append(m)
                        cont = cont + 1
        except:
            raise
        return sub

    def install_menu(self, *args):
        """
        Encontra os menus que devem ser inseridos para cada aplicação.
        return => retorna o menu com os ids para buscar as aplicações no banco.
        """
        import os

        application_install_class = "InstallApplication"
        title_application = "title_application"
        install_application = "install_application"
        diretorio = os.getcwd()
        menu = []
        for diret in os.listdir(diretorio):
            try:
                file = open(diretorio + "/" + diret + "/__init__.py", "r")
                file.close()
                try:
                    imp = __import__(
                        diret + ".models", globals={}, locals={}, fromlist=""
                    )
                except ImportError:
                    if eval(self.verbose):
                        print("O " + diret + ".models nao e um modulo valido!")
                    raise
                title = diret
                is_install = True
                for mod in dir(imp.models):
                    try:
                        if mod == application_install_class:
                            cls = "imp.models." + mod
                            try:
                                title = eval(cls + "." + title_application)
                            except:
                                pass
                            try:
                                is_install = eval(cls + "." + install_application)
                            except:
                                pass
                            ar = eval(cls + ".menu")
                            menu.append(self.lista(ar))
                    except:
                        pass
            except:
                pass
        return menu

    def install_applications(self, *args):
        applications = self.find_applications()
        try:
            if eval(args[0]):
                print("#Processando criacao das views de cada aplicacao no sistema...")
                for app in applications:
                    print("#View %s" % app[0])
                    print("create views\n %s %s %s" % (app[0], args[2], app[3]))
                    self.create_views(app[0], args[2], app[3])
                if eval(self.verbose):
                    print("#Pronto!")

            if eval(args[1]):
                print("#Processando instalacao das aplicacoes no sistema...")
                menu = self.install_menu()
                for app in applications:
                    print("\nInstalando aplicacao %s:" % app[0])
                    if self.install_application_view_db(app[0], "views", menu) == False:
                        print("Applicacao nao definida para instalacao ou falha!")
                    else:
                        if eval(self.verbose):
                            print("\t instalado com sucesso!")
        except:
            raise

    def create_views(self, *args):
        """
        Criando Views
        Instala as views de cada modelo de uma aplicacao específica.
        args[0] => application_install. Ex: 'folha'
        args[1] => Nome para o arquivo da view. Default: views.py
        args[2] => create_views = True/False
        """
        # print(u'create views\n %s %s %s' % (args[0], args[1], args[2]))
        application_install_class = "InstallApplication"
        application_install_class_create_views = "create_views"
        application_install_prefixo_controller = "prefixo_controller"
        meta_install_class = "InstallModel"
        meta_install_title_view = "title_view"
        meta_install_create_view = "create_view"
        meta_install_install_view = "install_view"
        meta_install_node_menu = "node_menu"
        model_install = "models"
        extend_class = "extjs.ExtCrud"
        application_install = args[0]
        try:
            create_all_views = args[2]
        except:
            create_all_views = False
        # print('create_all_views %s '%create_all_views)
        # TODO: receber application separado do model
        prefixo_controller = application_install
        install_model = application_install + "." + model_install
        module = ""
        title = ""
        node_menu = ""
        create_view = True
        install_view = True
        view_text = []
        if create_all_views:
            try:
                imp = __import__(install_model, globals={}, locals={}, fromlist="")
            except ImportError:
                raise
                return False

            cabecalho = []
            #        cabecalho.append(u"# -.- coding: utf-8 -.-")
            #        cabecalho.append(u"from contrib import extjs")
            #        cabecalho.append(u"from django import forms")
            #        cabecalho.append(u"from "+application_install+" import "+model_install+" as "+application_install+"_"+model_install)
            cabecalho.append("# -.- coding: utf-8 -.-\n")
            cabecalho.append("from contrib import extjs\n")
            cabecalho.append("from django import forms\n")
            cabecalho.append(
                "from "
                + application_install
                + " import "
                + model_install
                + " as "
                + application_install
                + "_"
                + model_install
                + "\n"
            )
            view_text.append(cabecalho)

            check = False
            for mod in dir(imp.models):
                if mod == application_install_class:
                    check = True
                    cls = "imp.models." + mod
                    try:
                        prefixo_controller = eval(
                            cls + "." + application_install_prefixo_controller
                        )
                    except:
                        if eval(self.verbose):
                            print(
                                "#Utilizando nome %s default para o controller."
                                % prefixo_controller
                            )
                    try:
                        check = eval(cls + "." + application_install_class_create_views)
                    except:
                        check = False
                        if eval(self.verbose):
                            print("#Criacao de views desabilitada.")

            if check == False:
                if eval(self.verbose):
                    print("#Criacao de views desabilitada.")
                return False

            for mod in dir(imp.models):
                cls = "imp.models." + mod
                for c in dir(eval(cls)):
                    if meta_install_class == c:
                        create_view = True
                        module = mod
                        try:
                            create_view = eval(
                                cls
                                + "."
                                + meta_install_class
                                + "."
                                + meta_install_create_view
                            )
                        except:
                            create_view = True
                        if create_view:
                            try:
                                title = eval(
                                    cls
                                    + "."
                                    + meta_install_class
                                    + "."
                                    + meta_install_title_view
                                )
                            except:
                                title = mod
                            try:
                                install_view = eval(
                                    cls
                                    + "."
                                    + meta_install_class
                                    + "."
                                    + meta_install_install_view
                                )
                            except:
                                install_view = True
                            try:
                                node_menu = eval(
                                    cls
                                    + "."
                                    + meta_install_class
                                    + "."
                                    + meta_install_node_menu
                                )
                            except:
                                node_menu = None
                            template = []
                            #                        template.append(u"\nclass "+prefixo_controller+module+"("+extend_class+"):")
                            #                        template.append(u"    class InstallMeta:")
                            #                        template.append(u"         controller = '"+prefixo_controller+module+"'")
                            #                        template.append(u"         title      = u'"+title+"'")
                            #                        template.append(u"         install   = "+str(install_view)+"\n")
                            #                        template.append(u"    class Form(forms.ModelForm):")
                            #                        template.append(u"        class Meta:")
                            #                        template.append(u"            model = "+application_install+"_"+model_install+"."+module+"\n")
                            #                        template.append(u"    titles = {")
                            #                        template.append(u"        'PANEL' : u'"+title+"',")
                            #                        template.append(u"        'LIST'  : u'Gerenciador de "+title+"',")
                            #                        template.append(u"        'NEW'   : u'Novo(a) "+title+"',")
                            #                        template.append(u"        'EDIT'  : u'Editando um(a) "+title+"',")
                            #                        template.append(u"        'DELETE': u'Removendo um(a) "+title+"',")
                            #                        template.append(u"        'FILTER': u'NOT_DEFINED_IN_CONTROLLER',")
                            #                        template.append(u"    }");
                            template.append(
                                "\nclass "
                                + prefixo_controller
                                + module
                                + "("
                                + extend_class
                                + "):\n"
                            )
                            template.append("    class InstallMeta:\n")
                            template.append(
                                "         controller = '"
                                + prefixo_controller
                                + module
                                + "'\n"
                            )
                            template.append("         title      = u'" + title + "'\n")
                            template.append(
                                "         node_menu  = u'" + node_menu + "'\n"
                            )
                            template.append(
                                "         install    = " + str(install_view) + "\n\n"
                            )
                            template.append("    class Form(forms.ModelForm):\n")
                            template.append("        class Meta:\n")
                            template.append(
                                "            model = "
                                + application_install
                                + "_"
                                + model_install
                                + "."
                                + module
                                + "\n\n"
                            )
                            template.append("    titles = {\n")
                            template.append("        'PANEL' : u'" + title + "',\n")
                            template.append(
                                "        'LIST'  : u'Gerenciador de " + title + "',\n"
                            )
                            template.append(
                                "        'NEW'   : u'Novo(a) " + title + "',\n"
                            )
                            template.append(
                                "        'EDIT'  : u'Editando um(a) " + title + "',\n"
                            )
                            template.append(
                                "        'DELETE': u'Removendo um(a) " + title + "',\n"
                            )
                            template.append(
                                "        'FILTER': u'NOT_DEFINED_IN_CONTROLLER',\n"
                            )
                            template.append("    }\n")
                            view_text.append(template)
            if self.write_file(self, application_install, view_text, args[1]):
                print("#Modelos instalados com Sucesso!")
            else:
                print("#Modelos não foram instalados!")
        else:
            if eval(self.verbose):
                print("View nao criada %s" % application_install)

    def write_file(self, *args):
        # TODO: quando for utilizado python na versão 3.0, haverá a possibilidade de escrever em arquivo através de estream, escapando do problema para escreve encode em texto
        """
        args[1] => application
        args[2] => texto do que deverá ser inserido na view
        args[3] => Nome do arquivo que deverá conter o conteúdo gerado.
        """
        import os

        application = args[1]
        texto = args[2]
        arquivo_nome = args[3]
        diretorio = os.getcwd()
        arquivo_diretorio = diretorio + "/" + application + "/" + arquivo_nome
        if eval(self.verbose):
            print('\n\n"""\n\tView da applicacao %s.\n"""' % application)
        try:
            FILE = open(arquivo_diretorio, "w")
            for t in texto:
                for ti in t:
                    if ti:
                        # print(ti.encode('utf-8'))
                        FILE.write(ti.encode("utf-8"))
            FILE.close()
        except:
            raise
            return False
        return True

    def find_applications(self):
        import os

        application_install_class = "InstallApplication"
        title_application = "title_application"
        install_application = "install_application"
        install_create_views = "create_views"
        applications = []
        app = []
        diretorio = os.getcwd()
        for diret in os.listdir(diretorio):
            app = None
            app = []
            try:
                file = open(diretorio + "/" + diret + "/__init__.py", "r")
                file.close()
                try:
                    imp = __import__(
                        diret + ".models", globals={}, locals={}, fromlist=""
                    )
                    app.append(diret)
                    title = diret
                    is_install = True
                    is_create_view = False
                    for mod in dir(imp.models):
                        try:
                            if mod == application_install_class:
                                cls = "imp.models." + mod
                                try:
                                    title = eval(cls + "." + title_application)
                                except:
                                    title = diret
                                try:
                                    is_install = eval(cls + "." + install_application)
                                except:
                                    is_install = True
                                try:
                                    is_create_view = eval(
                                        cls + "." + install_create_views
                                    )
                                except:
                                    is_create_view = False
                        except:
                            raise
                    app.append(title)
                    app.append(is_install)
                    app.append(is_create_view)
                    applications.append(app)
                except ImportError:
                    if eval(self.verbose):
                        print("O " + diret + ".models nao e um modulo valido!")
                    raise
            except:
                pass
        return applications

    def install_application_view_db(self, *args):
        """
        args[0] => application
        args[1] => view
        args[2] => menu
        """
        application_install = args[0]
        view_install = args[1]
        menu = args[2]
        meta_install_class = "InstallMeta"
        meta_install_title = "title"
        meta_install_controller = "controller"
        meta_install_install = "install"
        meta_install_node_menu = "node_menu"

        install_view = application_install + "." + view_install
        try:
            imp = __import__(install_view, globals={}, locals={}, fromlist="")
        except ImportError:
            print("Erro no import!\nFalha na instalacao da Aplicacao %s" % install_view)
            raise
            return False
        for vi in dir(imp.views):
            cls = "imp.views." + vi
            install = False
            for c in dir(eval(cls)):
                if meta_install_class == c:
                    try:
                        if eval(
                            cls + "." + meta_install_class + "." + meta_install_install
                        ):
                            install = eval(
                                cls
                                + "."
                                + meta_install_class
                                + "."
                                + meta_install_install
                            )
                    except:
                        install = False
                    try:
                        node_menu = eval(
                            cls
                            + "."
                            + meta_install_class
                            + "."
                            + meta_install_node_menu
                        )
                        if node_menu is None:
                            install = False
                    except:
                        install = False
                        print(
                            "Falha na instalacao do controller %s. Pois seu menu não foi definido corretamente!"
                            % vi
                        )
                        raise
                    if install:
                        application_id = self.busca_application_id(
                            menu, application_install, node_menu
                        )
                        if application_id:
                            obj_application = engine_models.Application.objects.get(
                                pk=application_id
                            )
                            try:
                                controller = engine_models.Controller()
                                controller.application = obj_application
                                controller.controller = eval(
                                    cls
                                    + "."
                                    + meta_install_class
                                    + "."
                                    + meta_install_controller
                                )
                                controller.title = eval(
                                    cls
                                    + "."
                                    + meta_install_class
                                    + "."
                                    + meta_install_title
                                )
                                controller.save()
                            except:
                                print("Falha na instalacao do controller %s" % vi)
                                raise
                        else:
                            print("Menu %s nao instalado." % node_menu)
        return True

    def install_engine_application(self, *args):
        """
        Inserindo uma aplicacao na base de dados.
        args[0] => título da aplicacao
        args[1] => título do sub aplicacao(default parâmetros)
        args[2] => True/False, instalar como aplicacao ou não
        """
        from engine.models import Application
        from engine.models import Controller

        title = args[0]
        subtitle = "Parâmetros"
        application_1 = None
        try:
            if args[1]:
                subtitle = args[1]
        except:
            pass
        try:
            application = engine_models.Application()
            application.active = True
            application.father = None
            application.title = title
            application.save()

            application_1 = engine_models.Application()
            application_1.active = True
            application_1.father = application
            application_1.title = subtitle
            application_1.save()

            nome = application.title + " -> " + application_1.title
            print("Aplicacao %s" % nome.encode("utf-8"))
        except:
            print("Falha na instalacao da Aplicacao %s" % title)
            raise
            return None
        return application_1.pk
