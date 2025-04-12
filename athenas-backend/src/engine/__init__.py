# -*- coding: utf-8 -*-
# from default.views import Application

"""Registro dos Javascripts para este aplicativo"""
# Application.register_javascript('/%(context)s/static/engine/js/core.js')
# Application.register_javascript('/%(context)s/static/engine/js/forms.js')
# Application.register_javascript('/%(context)s/static/engine/js/notification.js')
# Application.register_javascript('/%(context)s/static/js/crypto/md5.js')

"""Registro dos Stylesheet's para este aplicativo"""

default_app_config = "engine.apps.EngineConfig"


def post_install():
    from engine.models import Application, Controller

    # insert into engine_application(title, father_id, active) values('PAINEL DE CONTROLE', null, 1);
    # insert into engine_application(title, father_id, active) values('Funcionalidades', 1, 1);
    # insert into engine_application(title, father_id, active) values('Controle de Acesso', 1, 1);

    # insert into engine_controller(title, controller, application_id) values('Cadastro', 'ENGController', 2);
    # insert into engine_controller(title, controller, application_id) values('Grupo', 'ENGApplication', 2);
    # insert into engine_controller(title, controller, application_id) values('Grupo Permissão', 'ENGControllerPermission', 2);
    # insert into engine_controller(title, controller, application_id) values('Usuário', 'AUTHUser', 3);
    # insert into engine_controller(title, controller, application_id) values('Grupos', 'AUTHGroup', 3);

    control_panel, created = Application.objects.get_or_create(
        title="PAINEL DE CONTROLE",
        active=True,
        defaults={"title": "PAINEL DE CONTROLE", "active": True},
    )

    features, created = Application.objects.get_or_create(
        title="Funcionalidades",
        active=True,
        father=control_panel,
        defaults={"title": "Funcionalidades", "active": True, "father": control_panel},
    )

    access_control, created = Application.objects.get_or_create(
        title="Controle de Acesso",
        active=True,
        father=control_panel,
        defaults={
            "title": "Controle de Acesso",
            "active": True,
            "father": control_panel,
        },
    )

    for item in [
        ["Cadastro", "ENGController"],
        ["Grupo", "ENGApplication"],
        ["Grupo Permissão", "ENGControllerPermission"],
    ]:
        controller, created = Controller.objects.get_or_create(
            controller=item[1],
            defaults={"title": item[0], "controller": item[1], "application": features},
        )

    for item in [["Usuário", "AUTHUser"], ["Grupos", "AUTHGroup"]]:
        controller, created = Controller.objects.get_or_create(
            controller=item[1],
            defaults={
                "title": item[0],
                "controller": item[1],
                "application": access_control,
            },
        )
