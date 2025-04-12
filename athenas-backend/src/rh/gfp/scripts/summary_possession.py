# -*- coding: utf-8 -*-

from contrib.middleware import set_current_user
from rh.models import MovimentacaoRequisicao, Servidor

set_current_user("athenas")


def summary_exployee_by_possession(update_type=True, show_modified=False):
    tt = "XXX"
    ups = 0
    summary = {}

    q = Servidor.objects.all()

    for s in q.order_by("type_by_possession", "-ativo", "pessoa_fisica__nome"):
        pps = s.posses.filter().count()
        ppd = s.get_declarationactivity().count()
        ppr = MovimentacaoRequisicao.objects.filter(servidor=s).count()
        if (pps or ppd or ppr) and update_type:
            s._update_type_by_possession()

        if tt != s.type_by_possession:
            # print '>>> %s - %s' % (s.type_by_possession, s.get_type_by_possession_display())
            tt = s.type_by_possession

        if tt not in summary:
            summary[tt] = [s.get_type_by_possession_display(), 0, 0]
        summary[tt][1 if s.ativo else 2] += 1

        modified = "*" if "type_by_possession" in s.diff else ""

        if modified:
            if show_modified:
                print("%s: %s" % (s, s.diff))
            ups += 1

    print("UPDATEDS EMPLOYEES TYPE: %d" % ups)

    print("")
    # print '>>> SUMMARY'
    print(
        "\033[1;33m%03s   %-50s   %-9s %s\033[0m"
        % (">>>", "SUMMARY", "ATIVO", "INATIVO")
    )
    t_active = t_inactive = 0
    for tt in sorted(summary):
        print(
            "%03s - %-50s   %04d       %04d"
            % (tt, summary[tt][0], summary[tt][1], summary[tt][2])
        )
        t_active += summary[tt][1]
        t_inactive += summary[tt][2]
    print(
        "\033[1;33m%03s   %-50s   %04d       %04d\033[0m"
        % (">>>", "TOTAIS: ", t_active, t_inactive)
    )
