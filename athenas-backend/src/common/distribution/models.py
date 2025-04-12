# -*- coding: utf-8 -*-
import random
from datetime import datetime

from django.db import models
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User

from standard.models import AuditTimestampModel, Choice
from rh.models import OrgaoGeral
from contrib.middleware import get_current_user
from contrib.utils import getLogger


log = getLogger(__name__)


# _SNIPPET_ Decorador para Modelos com fields do tipo write once.
# Decorator for django models that contain write once fields.
def has_write_once_fields(target_class):
    def store_write_once_fields(sender, instance, **kwargs):
        if not instance.id:
            return

        for field_name in sender.write_once_fields:
            val = getattr(instance, field_name)
            setattr(instance, field_name + "_oldval", val)

    def check_write_once_fields(sender, instance, **kwargs):
        if not instance.id:
            return

        for field_name in sender.write_once_fields:
            old_value = getattr(instance, field_name + "_oldval")
            new_value = getattr(instance, field_name)
            if old_value != new_value:
                raise ValueError("Field '%s' is a write once field." % field_name)

    # for load
    models.signals.post_init.connect(store_write_once_fields, target_class, weak=False)

    # for save
    models.signals.post_save.connect(store_write_once_fields, target_class, weak=False)

    models.signals.pre_save.connect(check_write_once_fields, target_class, weak=False)

    return target_class


class Distribution(AuditTimestampModel):
    """
    Uma distribution é uma entidade que associa PARTICIPANTES
    (players) e PRÊMIOS/OBJETOS (rewards) a um determinado ORGÃO
    GERAL (localidade).
    """

    title = models.CharField(max_length=100, verbose_name="Título")
    origin = models.ForeignKey(
        OrgaoGeral,
        on_delete=models.PROTECT,
        verbose_name="Origem",
        related_name="distributions",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "distribution"
        verbose_name_plural = "distributions"

    class BaseError(Exception):
        def __init__(self, message, msg_type="error"):
            super(Distribution.BaseError, self).__init__(message)
            self.msg_type = msg_type

    def __str__(self):
        return "{id} : {title}".format(id=self.id, title=self.title)

    def copy_players_from(self, source):
        active_players = source.players.filter(active=True)

        if active_players.exists():
            with transaction.atomic():
                for player in active_players:
                    Player(title=player.title, distribution=self).save()
        else:
            raise Distribution.BaseError(
                message="Não há participantes ativos na distribuição de origem.",
                msg_type="warning",
            )


@has_write_once_fields
class Player(AuditTimestampModel):
    """
    Um player é um PARTICIPANTE que pode ser escolhido por meio
    de SORTEIO ou escolhido MANUALMENTE para receber um PRÊMIO/OBJETO.
    """

    title = models.CharField(max_length=100, verbose_name="Título")
    score = models.IntegerField(default=0, verbose_name="Pontos")
    accumulated_score = models.IntegerField(default=0, verbose_name="Pontos acumulados")
    active = models.BooleanField(default=True)
    distribution = models.ForeignKey(
        Distribution,
        on_delete=models.PROTECT,
        verbose_name="Distribuição",
        related_name="players",
    )

    # Para uso pelo decorator has_write_once_fields.
    write_once_fields = ("distribution",)

    class Meta:
        ordering = ["id"]
        verbose_name = "player"
        verbose_name_plural = "players"

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        if self.pk and self.rewards.exists():
            log.info(
                "Gestor de Distribuição (Player): Exclusão interceptada. "
                "Marcando Player '%s' como inativo." % self
            )

            # Se player tem rewards, torna-o inativo
            # ao invés de tentar removê-lo.
            self.active = False
            self.save()

            raise Exception(
                "Este Participante não será removido, mas "
                "apenas marcado como inativo, pois existem "
                "Objetos associados a ele."
            )

        super(Player, self).delete(*args, **kwargs)

    def refresh_activation(self):
        query = self.distribution.rewards.filter(winner=None)
        for reward in query.all():
            reward.reset_match()

    def save(self, *args, **kwags):
        changed_activation = None

        if self.pk:
            older = self.__class__.objects.get(pk=self.pk)
            if older.active != self.active:
                changed_activation = self.active

        super(Player, self).save(*args, **kwags)

        if changed_activation is not None:
            self.refresh_activation()


@has_write_once_fields
class Reward(AuditTimestampModel):
    """
    Um reward é uma entidade que representa um PRÊMIO ou
    OBJETO a ser distribuído por SORTEIO ou MANUALMENTE.
    """

    title = models.CharField(max_length=100, verbose_name="Título")
    distributed_at = models.DateTimeField(
        verbose_name="Distribuído em", blank=True, null=True
    )
    distributed_manually = models.BooleanField(
        default=False, verbose_name="Método de Distribuição"
    )
    external_number = models.CharField(
        max_length=100, verbose_name="Número Externo", blank=True, null=True
    )
    winner = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        verbose_name="Escolhido",
        related_name="as_winner_of_rewards",
        blank=True,
        null=True,
    )
    distribution = models.ForeignKey(
        Distribution,
        on_delete=models.PROTECT,
        verbose_name="Distribuição",
        related_name="rewards",
    )
    distributed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Distribuído por",
        related_name="distributed_rewards",
        blank=True,
        null=True,
    )
    players = models.ManyToManyField(
        Player, related_name="rewards", through="distribution.Match"
    )
    canceled_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Cancelado por",
        related_name="canceled_distributions",
        blank=True,
        null=True,
    )
    canceled_at = models.DateTimeField(
        verbose_name="Cancelado em", blank=True, null=True
    )

    # Para uso pelo decorator has_write_once_fields.
    write_once_fields = ("distribution",)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "reward"
        verbose_name_plural = "rewards"

    def __str__(self):
        return "{id} : {title}".format(id=self.id, title=self.title)

    def distribute(self):
        if self.is_already_distributed():
            raise Exception(
                "Não foi possível concluir a ação "
                "pois o Objeto já foi distribuído. "
                "Objeto em questão: '%s'." % self
            )

        query = self.matches.filter(incident_type__in=(2, 3))

        if query.exists() and query.count() == 1:
            log.info("Gestor de Distribuição (Reward): Temos um incidente positivo.")
            self.delivery(query.get().player)
        elif query.exists() and query.count() > 1:
            raise Exception(
                "Temos dois incidentes de direcionamento de "
                "distribuição e só é permitido apenas um."
            )
        else:
            query = self.matches.exclude(incident_type__in=(4, 5)).exclude(
                player__active=False
            )
            num_cards = max([match.player.score for match in query]) + 1
            num_players = query.count()

            log.info(
                "Gestor de Distribuição (Reward): Cards/Player: %d," " Players: %d",
                num_cards,
                num_players,
            )

            cards = []
            for match in query:
                cards += [match.player] * (num_cards - match.player.score)

            log.info("Gestor de Distribuição (Reward): Cards: %d", len(cards))
            selected = cards[random.randint(1, 1000000) % len(cards)]
            self.delivery(selected)

    def balance_score_of_players(self):
        min_score = None
        for player_score in [match.player.score for match in self.matches.all()]:
            if min_score is None:
                min_score = player_score
            else:
                min_score = player_score if player_score < min_score else min_score

        if min_score > 0:
            log.info("Gestor de Distribuição (Reward): We need to reset the scores.")
            for match in self.matches.all():
                match.player.score = match.player.score - min_score
                match.player.save()

    def distribute_for_player(self, player):
        if self.is_already_distributed():
            raise Exception(
                "Não foi possível concluir a ação "
                "pois o Objeto já foi distribuído. "
                "Objeto em questão: '%s'." % self
            )

        self.delivery(player, True)

    def delivery(self, player, manually=False):
        if not self.is_already_distributed():
            with transaction.atomic():
                self.winner = player
                self.distributed_manually = manually
                self.distributed_by = get_current_user()
                self.distributed_at = datetime.now()
                self.save()

                player.score += 1
                player.accumulated_score += 1
                player.save()

                self.balance_score_of_players()
        else:
            raise Exception(
                "Não foi possível concluir a ação "
                "pois o Objeto já foi distribuído. "
                "Objeto em questão: '%s'." % self
            )

    def is_already_distributed(self):
        is_being_created = self.pk is None
        if is_being_created:
            return False

        log.info(
            "Gestor de Distribuição (Reward): Verificando "
            "se Reward '%s' já foi distribuído." % self
        )

        if self.winner is None:
            return False

        criterion = Q(id=self.pk) & ~Q(winner=None)
        return Reward.objects.filter(criterion).exists()

    def _validate_winner(self):
        if self.winner:
            if not self.distribution.players.filter(pk=self.winner.pk).exists():
                raise Exception(
                    "Não foi possível distribuir o Objeto '%s' ao "
                    "Participante '%s', pois ambos pertencem a "
                    "Distribuições diferentes." % (self, self.winner)
                )

            if not self.winner.active:
                raise Exception(
                    "Não foi possível distribuir o Objeto '%s' ao "
                    "Participante '%s', pois este último não está "
                    "ativo." % (self, self.winner)
                )

    def reset_match(self):
        self.matches.all().delete()
        Match.objects.bulk_create(
            [
                Match(reward=self, player=player)
                for player in self.distribution.players.filter(active=True)
            ]
        )

    def save(self, *args, **kwargs):
        skip = getattr(self, "skip_is_already_distributed", False)
        if self.is_already_distributed() and not skip:
            raise Exception(
                "Não foi possível concluir a ação pois o Objeto "
                "já foi distribuído. Objeto em questão: '%s'." % self
            )

        self._validate_winner()

        is_being_created = self.pk is None
        super(Reward, self).save(*args, **kwargs)

        if is_being_created:
            self.reset_match()

    def delete(self, *args, **kwargs):
        if self.is_already_distributed():
            raise Exception(
                "Não é possível remover um Objeto que já foi "
                "distribuído. Objeto em questão: '%s'. " % self
            )

        super(Reward, self).delete(*args, **kwargs)

    def was_distribution_canceled(self):
        return self.canceled_by is not None

    def cancel_distribution(self):
        log.info(
            "Gestor de Distribuição (Reward): Tentando cancelar "
            "distribuicao do Reward '%s'." % self
        )

        if self.was_distribution_canceled():
            raise Exception(
                "O Objeto já estava cancelado. "
                "Objeto em questão: '%s'. "
                "Ação abortada." % self
            )
        elif not self.is_already_distributed():
            raise Exception(
                "Não é possível cancelar a distribuição "
                "de um Objeto ainda não distribuído. "
                "Objeto em questão: '%s'. "
                "Ação abortada." % self
            )
        else:
            self.skip_is_already_distributed = True

            self.canceled_by = get_current_user()
            self.canceled_at = datetime.now()
            self.save()

            self.winner.score -= 1
            self.winner.accumulated_score -= 1
            self.winner.save()


@has_write_once_fields
class Match(models.Model):
    """
    Um match é uma entidade que representa uma PARTIDA, sendo que nessa
    partida serão registrados o PRÊMIO e os PARTICIPANTES de um SORTEIO,
    bem como o TIPO DE INCIDENTE associado a cada PARTICIPANTE.
    """

    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        verbose_name="Participante",
        related_name="matches",
    )
    reward = models.ForeignKey(
        Reward, on_delete=models.CASCADE, verbose_name="Objeto", related_name="matches"
    )
    incident_details = models.TextField(
        null=True, blank=True, verbose_name="Detalhes do Incidente"
    )

    """
    Tipos de Incidente:
        1 = Sem incidente
        2 = Conexão
        3 = Prevenção
        4 = Impedimento
        5 = Suspeição

    Como cadastrar:
        Menu Athenas -> PAINEL DE CONTROLE -> Parâmetros de Sistema
    """
    incident_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("distribution", "INCIDENT_TYPE"),
        default=1,
        verbose_name="Tipo de Incidente",
    )

    # Para uso pelo decorator has_write_once_fields.
    write_once_fields = (
        "player",
        "reward",
    )

    class Meta:
        verbose_name = "match"
        verbose_name_plural = "matches"

    def __str__(self):
        text = "Participante cod. {player} concorrendo ao Objeto cod. {reward}"
        return text.format(player=self.player.id, reward=self.reward.id)

    def save(self, *args, **kwargs):
        if self.pk and self.reward.is_already_distributed():
            raise Exception(
                "Não e possível editar um Objeto que já foi "
                "distribuído. Objeto em questão '%s'." % self.reward
            )

        # incident_type do tipo 'Sem incidente' não precisa de detalhes.
        if self.incident_type == 1:
            self.incident_details = None
            log.info(
                "Gestor de Distribuição (Match): Anulando "
                "incident_details para o incident_type 1."
            )

        super(Match, self).save(*args, **kwargs)
