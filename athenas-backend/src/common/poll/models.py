# -*- coding:utf-8 -*-
import datetime
from django.db import models
from django.contrib.auth.models import User

from contrib.utils import getLogger, employee_from_user


log = getLogger(__name__)


def breaker(instance):
    poll = getattr(instance, "poll", None) or instance
    if poll.is_locked():
        raise Exception(
            "Não é permitida alteração desta votação porque, ou está em andamento ou já foi finalizada."
        )


class PollConditions(models.Model):
    expression = models.CharField(max_length=300)
    value = models.CharField(max_length=300, null=True)
    description = models.CharField(max_length=300)

    def __str__(self):
        return str(self.description)


class Poll(models.Model):
    title = models.CharField("Título da votação", max_length=300)
    max_of_choices = models.IntegerField(
        "Quantidade de votos permitidos", default=1, db_index=True
    )
    publication_start = models.DateTimeField(
        "Inicio da publicação", null=True, db_index=True
    )
    publication_end = models.DateTimeField(
        "Fim da publicação", null=True, db_index=True
    )
    create_date = models.DateTimeField(
        "Data de criação", db_index=True, auto_now_add=True
    )
    active = models.BooleanField("Ativa", default=True, db_index=True)
    users_who_voted = models.ManyToManyField(User, related_name="safe_poll_voted")
    conditions = models.ManyToManyField(PollConditions, related_name="polls")
    updating_allowed_list = models.BooleanField(default=False)

    def can_vote_by(self, user):
        # return self.test_user_conditions(user) and not self.is_in_blacklist(user)
        if self.allowed_list:
            return self.allowed_list.allowed_users.filter(pk=user.pk).exists()
        return False

    def has_publication(self):
        # log.info('%s has_publication = %s' % (self, bool(self.publication_start and self.publication_end)))
        return bool(self.publication_start and self.publication_end)

    def is_published(self):
        now = datetime.datetime.now()
        # log.info(self.publication_start)
        # log.info(now)
        # log.info(self.publication_end)
        # log.info('%s is_published = %s' % (self, self.has_publication() and self.publication_start <= now <= self.publication_end))
        return (
            self.has_publication()
            and self.publication_start <= now <= self.publication_end
        )

    def is_finished(self):
        now = datetime.datetime.now()
        # log.info(now)
        # log.info(self.publication_end)
        check = bool(self.has_publication() and now > self.publication_end)
        # log.info('%s is_finished = %s' % (self, check))
        return check

    def is_on(self):
        # log.info('%s is_on %s' % (self, self.is_published() and not self.is_finished()))
        return self.is_published() and not self.is_finished()

    def is_locked(self):
        # log.info('%s is_locked %s' % (self, self.is_published() or self.is_finished()))
        return self.is_published() or self.is_finished()

    def is_valid(self):
        return (
            self.choices.filter(active=True, meta=False).count() >= self.max_of_choices
        )

    def is_in_blacklist(self, user):
        try:
            return self.blacklist.blocked_users.filter(id=user.id).exists()
        except Exception:
            return False

    def test_user_conditions_expressions(self):
        for condition in self.conditions.all():
            for expression in condition.expression.split("|"):
                self.test_user_condition_expression(expression)
        return True

    def test_user_condition_expression(self, expression):
        pieces = expression.split(":")
        if len(pieces) != 2:
            raise Exception(
                "Expressão para definição de publico alvo está mal formada. Contate o departamento de TI."
            )
        return True

    def test_user_conditions(self, user):
        conditions = []
        employee = employee_from_user(user, False)
        if employee:
            for condition in self.conditions.all():
                for expression in condition.expression.split("|"):
                    self.test_user_condition_expression(expression)
                    attr, value = expression.split(":")
                    val = getattr(employee, attr, None)
                    if callable(val):
                        val = val()
                    conditions.append(val == eval(value))
            # conditions.append( employee.is_ativo() )
        return len(conditions) > 0 and all(conditions)

    def was_counted(self):
        # return self.votes.filter(counted=True).exists() or getattr(self, '_counted', False)
        return (
            CountedPolls.objects.filter(poll=self).exists()
            or self.votes.filter(counted=True).exists()
        )

    def was_voted_by(self, user):
        return self.users_who_voted.filter(username=user.username).exists()

    @classmethod
    def polls_by_user(self, user):
        def checker(poll, user):
            return (
                poll.can_vote_by(user)
                and poll.is_valid()
                and not poll.was_voted_by(user)
            )

        now = datetime.datetime.now()
        kwargs = dict(active=True, publication_start__lte=now, publication_end__gte=now)

        return [
            poll
            for poll in Poll.objects.filter(**kwargs).order_by("-id")
            if checker(poll, user)
        ]

    def save(self, *args, **kwargs):
        breaker(self)
        super(Poll, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        breaker(self)
        super(Poll, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.title)


class CountedPolls(models.Model):
    poll = models.OneToOneField(
        Poll, related_name="counted_poll", on_delete=models.CASCADE
    )


class BlackList(models.Model):
    # Parametro "on_delete" adicionado. (Django 2)
    poll = models.OneToOneField(
        Poll, related_name="blacklist", null=True, on_delete=models.CASCADE
    )
    blocked_users = models.ManyToManyField(User, related_name="safe_poll_blacklists")


class AllowedList(models.Model):
    poll = models.OneToOneField(
        Poll, related_name="allowed_list", null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    allowed_users = models.ManyToManyField(User, related_name="safe_poll_allowed_lists")


class Choice(models.Model):
    choice = models.CharField("Alternativa", max_length=300)
    meta = models.BooleanField("Meta opção de voto", default=False, db_index=True)
    poll = models.ForeignKey(
        Poll, verbose_name="Enquete", related_name="choices", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    active = models.BooleanField("Ativo", default=True, db_index=True)

    def save(self, *args, **kwargs):
        breaker(self)
        super(Choice, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        breaker(self)
        super(Choice, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.choice)


class Votes(models.Model):
    poll = models.ForeignKey(
        Poll, related_name="votes", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    choice = models.ForeignKey(
        Choice, related_name="votes", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    counted = models.BooleanField(default=False, db_index=True)
    authentic = models.BooleanField(default=False, db_index=True)
    signature = models.CharField(max_length=300)

    def __str__(self):
        return "%s|%s|%s - counted: %s, valid: %s" % (
            self.id,
            self.poll.id,
            self.choice.id,
            self.counted,
            self.authentic,
        )
