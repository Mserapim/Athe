# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.middleware import get_current_user
from contrib.utils import getLogger, employee_from_user
from common.distribution.models import Reward
from django.db.transaction import atomic


log = getLogger(__name__)


class CDReward(RestfulDRY):

    _model = Reward

    force_upper = False

    full_text_index = ("title__icontains", "external_number__icontains")

    def get_query(self, *args, **kwags):
        query = super(CDReward, self).get_query(*args, **kwags)

        employee = employee_from_user(get_current_user())
        if employee:
            query = query.filter(
                distribution__origin__in=employee.work_locations_effective_exercise
            )
        else:
            query = query.none()

        return query

    def reset_match(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            reward = self.get_query().get(pk=args[0])
            reward.reset_match()

            rst.update(success=True, message="atendimento atendido")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def distribute(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            with atomic():
                pkset = self.get_params().get("pkset")
                pkset = pkset if isinstance(pkset, (tuple, list)) else [pkset]

                for reward in self.get_query().filter(pk__in=pkset):
                    reward.distribute()
            rst.update(message="Objetos distribuidos com sucesso.", success=True)
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def distribute_manually(self, args=[]):
        rst = {
            "success": False,
            "message": "Action not implemented.",
        }

        try:
            with atomic():
                pkset = self.get_params().get("pkset")
                pkset = pkset if isinstance(pkset, (tuple, list)) else [pkset]

                for reward in self.get_query().filter(pk__in=pkset):
                    player = reward.players.get(pk=self.get_params().get("player"))
                    # log.info('Gestor de Distribuicao: chosen: %s, players: %s' % (player, reward.players.all()))
                    reward.distribute_for_player(player)

                rst.update(message="Objetos distribuidos com sucesso.", success=True)
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        return self.renderer(rst)

    def cancel_distribution(self, args=[]):
        rst = {"success": False, "message": "Action not implemented."}

        try:
            with atomic():
                pkset = self.get_params().get("pkset")
                pkset = pkset if isinstance(pkset, (tuple, list)) else [pkset]

                for reward in self.get_query().filter(pk__in=pkset):
                    reward.cancel_distribution()

            rst.update(message="Distribuições canceladas", success=True)
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        return self.renderer(rst)
