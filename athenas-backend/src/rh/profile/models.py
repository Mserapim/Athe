# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group, Permission, User
from django.db import models
from django.db.models.signals import m2m_changed, post_delete, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify


from contrib.middleware import get_current_user
from contrib.utils import getLogger
from engine.models import ControllerPermission
from rh.models import DeclaracaoAtividade, Lotacao, Servidor, ServidorLotacao

log = getLogger(__name__)


class JobProfile(models.Model):
    codename = models.CharField(
        max_length=100, db_index=True, unique=True, verbose_name="Identificador"
    )
    workplace = models.ForeignKey(
        "rh.lotacao",
        related_name="in_job_profiles",
        verbose_name="Lotação",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    for_leadership = models.BooleanField(verbose_name="Para chefia", default=False)
    for_workplace = models.BooleanField(verbose_name="Para lotação", default=False)
    for_work_assignment = models.BooleanField(
        verbose_name="Para designação", default=False
    )
    for_activity_statement = models.BooleanField(
        verbose_name="Para declaração de atividade", default=False
    )
    permissions = models.ManyToManyField(Permission, related_name="in_job_profiles")
    groups = models.ManyToManyField(Group, related_name="in_job_profiles")
    features = models.ManyToManyField(
        ControllerPermission, related_name="in_job_profiles"
    )
    linked_workplaces = models.ManyToManyField(
        Lotacao, related_name="in_linked_job_profile"
    )

    class Meta:
        permissions = (
            ("sync_grants_for_user", "Pode sincronizar as permissões para um usuario"),
            (
                "sync_grants_for_user_all_profiles",
                "Pode sincronizar as permissões de todos os profiles",
            ),
        )

    def __str__(self):
        return self.codename

    @property
    def affected_users(self):
        return User.objects.filter(servidor__in=self.affected_employers)

    @property
    def affected_employers(self):
        if not hasattr(self, "__cache_affected_employers"):
            pkset = []

            query = self.affected_employers_for_workplace
            pkset += query.values("pk") if query.exists() else []

            query = self.affected_employers_for_work_assignment
            pkset += query.values("pk") if query.exists() else []

            query = self.affected_employers_for_leadership
            pkset += query.values("pk") if query.exists() else []

            # FIXME: As informações em DeclaracaoAtividade estão depreciadas
            # query = self.affected_employers_for_activity_statement
            # pkset += query.values('pk') if query.exists() else []

            self.__cache_affected_employers = Servidor.objects.filter(
                pk__in=[pkinfo.get("pk") for pkinfo in pkset]
            )

        return self.__cache_affected_employers

    def _get_all_assignment_documents(self):
        # _get_all_assignment_documents_REFACTORING
        if not hasattr(self, "__cache_get_all_assignment_documents"):
            self.__cache_get_all_assignment_documents = (
                ServidorLotacao.work_assignment_exercise().filter(
                    lotacao__in=self.linked_workplaces.filter()
                )
            )
        return self.__cache_get_all_assignment_documents

    @property
    def affected_employers_for_workplace(self):
        if (
            not hasattr(self, "__cache_affected_employers_for_workplace")
            and self.for_workplace
        ):
            docs = self._get_all_assignment_documents().exclude(designacao=True)
            employers = Servidor.objects.filter(
                pk__in=docs.values("movimentacao_posse__servidor__pk")
            )

            self.__cache_affected_employers_for_workplace = employers.filter(ativo=True)
        else:
            self.__cache_affected_employers_for_workplace = Servidor.objects.none()

        return self.__cache_affected_employers_for_workplace

    @property
    def affected_employers_for_work_assignment(self):
        if (
            not hasattr(self, "__cache_affected_employers_for_work_assignment")
            and self.for_work_assignment
        ):
            docs = self._get_all_assignment_documents().filter(designacao=True)
            employers = Servidor.objects.filter(
                pk__in=docs.values("movimentacao_posse__servidor__pk")
            )

            self.__cache_affected_employers_for_work_assignment = employers.filter(
                ativo=True
            )
        else:
            self.__cache_affected_employers_for_work_assignment = (
                Servidor.objects.none()
            )

        return self.__cache_affected_employers_for_work_assignment

    @property
    def affected_employers_for_activity_statement(self):
        # FIXME: As informações em DeclaracaoAtividade estão depreciadas
        if (
            not hasattr(self, "__cache_affected_employers_for_activity_statement")
            and self.for_activity_statement
        ):
            docs = DeclaracaoAtividade.objects.filter(
                ativo=True, lotacao__in=self.linked_workplaces.filter()
            )
            self.__cache_affected_employers_for_activity_statement = (
                Servidor.objects.filter(pk__in=docs.values("servidor__pk"), ativo=True)
            )
        else:
            self.__cache_affected_employers_for_activity_statement = (
                Servidor.objects.none()
            )

        return self.__cache_affected_employers_for_activity_statement

    @property
    def affected_employers_for_leadership(self):
        if (
            not hasattr(self, "__cache_affected_employers_for_leadership")
            and self.for_leadership
        ):
            self.__cache_affected_employers_for_leadership = Servidor.objects.filter(
                responsavel_por__in=self.linked_workplaces.filter()
            )
        else:
            self.__cache_affected_employers_for_leadership = Servidor.objects.none()

        return self.__cache_affected_employers_for_leadership

    def sync_grants_for_user(self, user, action="add", to_exclude=None):
        log.info(
            "Sincronizando permissões para %s no profile %s com a ação: %s",
            user,
            self.codename,
            action,
        )

        table = {}

        current_user = get_current_user()

        if not current_user.has_perm("profile.sync_grants_for_user"):
            raise Exception("Usuário não possui permissão para executar a ação")

        if action == "add" and user:
            table.update(
                permission={
                    "message": "Processando permissões diretas...",
                    "message_action": "Adicionando permissão direta %s",
                    "query": self.permissions.exclude(
                        pk__in=user.user_permissions.filter()
                    ),
                    "method": user.user_permissions.add,
                },
                group={
                    "message": "Processando grupos de acesso...",
                    "message_action": "Adicionando grupo de permissão %s",
                    "query": self.groups.exclude(pk__in=user.groups.filter()),
                    "method": user.groups.add,
                },
                feature={
                    "message": "Processando permissões de funcionalidades...",
                    "message_action": "Adicionando permissão de funcionalidade %s",
                    "query": self.features.exclude(
                        pk__in=user.controllerpermission_set.filter()
                    ),
                    "method": user.controllerpermission_set.add,
                },
            )
        elif action == "remove" and user:
            table.update(
                permission={
                    "message": "Processando permissões diretas...",
                    "message_action": "Removendo permissão direta %s",
                    "query": user.user_permissions.filter(
                        pk__in=[obj.pk for obj in self.permissions.filter()]
                    ),
                    "method": user.user_permissions.remove,
                },
                group={
                    "message": "Processando grupos de acesso...",
                    "message_action": "Removendo grupo de permissão %s",
                    "query": user.groups.filter(
                        pk__in=[obj.pk for obj in self.groups.filter()]
                    ),
                    "method": user.groups.remove,
                },
                feature={
                    "message": "Processando permissões de funcionalidades...",
                    "message_action": "Removendo permissão de funcionalidade %s",
                    "query": user.controllerpermission_set.filter(
                        pk__in=[obj.pk for obj in self.features.filter()]
                    ),
                    "method": user.controllerpermission_set.remove,
                },
            )

        for key, step in list(table.items()):
            step = table.get(key)
            fn = step.get("method")

            for permission in step.get("query"):
                log.info(step.get("message_action", "") % permission)
                fn(permission)

        if action == "remove":
            self.sync_grants_for_user_all_profiles(user, to_exclude=to_exclude)

    @classmethod
    def sync_grants_for_user_all_profiles(klass, user, to_exclude=None):
        current_user = get_current_user()

        if not current_user.has_perm("profile.sync_grants_for_user_all_profiles"):
            raise Exception("Usuário não possui permissão para executar a ação")

        employee = Servidor.from_user(user)

        if employee:
            query = klass.objects.filter(linked_workplaces__in=employee.work_locations)
            # to_exclude comentado pois estava retirando as permissões concedidas da lotação e não só do exercício inativo
            # tentar outra abordagem
            # if to_exclude:
            #     query = query.exclude(linked_workplaces__pk=to_exclude.pk)
            for profile in query.distinct():
                if user in profile.affected_users and employee.is_ativo():
                    profile.sync_grants_for_user(user)

    def sync_grants(self):
        for user in self.affected_users:
            self.sync_grants_for_user(user)

    def save(self, *args, **kwargs):
        self.codename = slugify(self.codename)
        super(JobProfile, self).save(*args, **kwargs)

        if not self.linked_workplaces.filter(pk=self.workplace.pk).exists():
            self.linked_workplaces.add(self.workplace)

    @classmethod
    def signal_m2m_changed_permissions(
        klass, instance, action, pk_set, *args, **kwargs
    ):
        if action in ("post_add", "post_remove", "pre_clear"):
            for user in instance.affected_users:
                log.info("Sincronizando permissões de acesso para %s", user)
                perms = []

                if action == "post_add":
                    perms = Permission.objects.filter(pk__in=pk_set).exclude(
                        pk__in=[cperm.pk for cperm in user.user_permissions.filter()]
                    )
                elif action == "post_remove":
                    perms = user.user_permissions.filter(pk__in=pk_set)
                elif action == "pre_clear":
                    perms = user.user_permissions.filter(
                        pk__in=[perm for perm in instance.permissions.filter()]
                    )

                for perm in perms:
                    if action == "post_add":
                        log.info("Adicionando a permissão %s", perm)
                        user.user_permissions.add(perm)
                    elif action in ("post_remove", "pre_clear"):
                        log.info("Retirando a permissão %s", perm)
                        user.user_permissions.remove(perm)

    @classmethod
    def signal_m2m_changed_groups(klass, instance, action, pk_set, *args, **kwargs):
        if action in ("post_add", "post_remove", "pre_clear"):
            for user in instance.affected_users:
                log.info("Sincronizando grupos de acesso para %s", user)
                groups = []

                if action == "post_add":
                    groups = Group.objects.filter(pk__in=pk_set).exclude(
                        pk__in=[group.pk for group in user.groups.filter()]
                    )
                elif action == "post_remove":
                    groups = user.groups.filter(pk__in=pk_set)
                elif action == "pre_clear":
                    groups = user.groups.filter(
                        pk__in=[group.pk for group in instance.groups.filter()]
                    )

                for group in groups:
                    if action == "post_add":
                        log.info("Adicionando o grupo de permissão %s", group)
                        user.groups.add(group)
                    elif action in ("post_remove", "pre_clear"):
                        log.info("Retirando o grupo de permissão %s", group)
                        user.groups.remove(group)

    @classmethod
    def signal_m2m_changed_features(klass, instance, action, pk_set, *args, **kwargs):
        if action in ("post_add", "post_remove", "pre_clear"):
            for user in instance.affected_users:
                log.info("Sincronizando grupos de acesso para %s", user)
                cont_perms = []

                if action == "post_add":
                    cont_perms = ControllerPermission.objects.filter(
                        pk__in=pk_set
                    ).exclude(
                        pk__in=[
                            cperm.pk for cperm in user.controllerpermission_set.filter()
                        ]
                    )
                elif action == "post_remove":
                    cont_perms = user.controllerpermission_set.filter(pk__in=pk_set)
                elif action == "pre_clear":
                    cont_perms = user.controllerpermission_set.filter(
                        pk__in=[cont_perm for cont_perm in instance.features.filter()]
                    )

                for cont_perm in cont_perms:
                    if action == "post_add":
                        log.info("Adicionando o grupo de permissão %s", cont_perm)
                        user.controllerpermission_set.add(cont_perm)
                    elif action in ("post_remove", "pre_clear"):
                        log.info("Retirando o grupo de permissão %s", cont_perm)
                        user.controllerpermission_set.remove(cont_perm)

    @classmethod
    def signal_m2m_changed_linked_workplaces(
        klass, instance, action, pk_set, *args, **kwargs
    ):
        log.debug([instance, action, pk_set, "linked_workplaces"])

    @classmethod
    def signal_save_employee_location(klass, instance, *args, **kwargs):
        query = None
        # older = ServidorLotacao.objects.get(pk=instance.pk) if instance.pk else None
        older = None
        if ServidorLotacao.objects.filter(pk=instance.pk).exists():
            older = ServidorLotacao.objects.get(pk=instance.pk)

        action = None
        if older:
            if older.ativo != instance.ativo and older.ativo:
                action = "remove"
            elif older.ativo != instance.ativo and not older.ativo:
                action = "add"
        else:
            action = "add" if instance.ativo else "remove"
        if kwargs.get("_remove", False) or not action:
            action = "remove"

        to_exclude = None
        if not instance.ativo:
            to_exclude = instance.lotacao

        base = instance if not older else older

        query = (
            klass.objects.filter(linked_workplaces=base.lotacao)
            .filter(for_leadership=False)
            .filter(for_activity_statement=False)
        )

        if base.designacao:
            query = query.filter(for_work_assignment=True)
        else:
            query = query.filter(for_workplace=True)

        if action:
            for profile in query:
                profile.sync_grants_for_user(
                    base.servidor.user, action, to_exclude=to_exclude
                )
        else:
            log.info(
                "Sem mudanças de permissão com esta edição de declaração de atividade."
            )

    @classmethod
    def signal_save_activity_statement(klass, instance, *args, **kwargs):
        query = None
        older = None
        if DeclaracaoAtividade.objects.filter(pk=instance.pk).exists():
            older = DeclaracaoAtividade.objects.get(pk=instance.pk)

        action = None
        if older:
            if older.ativo != instance.ativo and older.ativo:
                action = "remove"
            elif older.ativo != instance.ativo and not older.ativo:
                action = "add"
        else:
            action = "add" if instance.ativo else "remove"
        if kwargs.get("_remove", False) or not action:
            action = "remove"

        to_exclude = None
        if not instance.ativo:
            to_exclude = instance.lotacao

        base = instance if not older else older
        if action:
            query = klass.objects.filter(
                linked_workplaces=base.lotacao, for_activity_statement=True
            )
            for profile in query:
                profile.sync_grants_for_user(
                    base.servidor.user, action, to_exclude=to_exclude
                )
        else:
            log.info(
                "Sem mudanças de permissão com esta edição de declaração de atividade."
            )

    @classmethod
    def signal_save_location_leadership(klass, instance, *args, **kwargs):
        older = Lotacao.objects.get(pk=instance.pk) if instance.pk else None

        new_user = instance.responsavel.user if instance.responsavel else None
        older_user = older.responsavel.user if older and older.responsavel else None

        if older_user == new_user:
            return

        if instance.pk:
            for profile in instance.in_linked_job_profile.filter(for_leadership=True):
                new_user and profile.sync_grants_for_user(new_user, action="add")
                older_user and profile.sync_grants_for_user(older_user, action="remove")


m2m_changed.connect(
    JobProfile.signal_m2m_changed_permissions, sender=JobProfile.permissions.through
)
m2m_changed.connect(
    JobProfile.signal_m2m_changed_groups, sender=JobProfile.groups.through
)
m2m_changed.connect(
    JobProfile.signal_m2m_changed_features, sender=JobProfile.features.through
)
m2m_changed.connect(
    JobProfile.signal_m2m_changed_linked_workplaces,
    sender=JobProfile.linked_workplaces.through,
)

pre_save.connect(JobProfile.signal_save_location_leadership, sender=Lotacao)
pre_save.connect(JobProfile.signal_save_employee_location, sender=ServidorLotacao)


@receiver(post_delete, sender=ServidorLotacao)
def pre_delete_perm(sender, instance, **kwargs):
    kwargs.update({"_remove": True})
    if sender == ServidorLotacao:
        JobProfile.signal_save_employee_location(instance, **kwargs)
    if sender == DeclaracaoAtividade:
        JobProfile.signal_save_activity_statement(instance, **kwargs)
