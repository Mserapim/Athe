from rh.gfp.models import ContraCheque, FolhaEvento

contracheques = [
    8651974,
    8651925,
    8651920,
    8651894,
    8651695,
    8651562,
    8651493,
    8651458,
    8647972,
    8647704,
    8646708,
    8644753,
    8644753,
    8644620,
    8644378,
    8634961,
    8628999,
]
cc_evento = {
    8651974: [
        "99101",
    ],
    8651925: [
        "99101",
    ],
    8651920: [
        "99101",
    ],
    8651894: [
        "99101",
    ],
    8651695: [
        "99101",
    ],
    8651562: [
        "99101",
    ],
    8651493: [
        "99101",
    ],
    8651458: [
        "99101",
    ],
    8647972: [
        "53000",
    ],
    8647704: [
        "53000",
    ],
    8646708: [
        "05700",
    ],
    8644753: ["53100", "53600"],
    8644620: [
        "50520",
    ],
    8644378: [
        "53100",
    ],
    8634961: [
        "51000",
    ],
    8628999: [
        "90501",
    ],
}

cc_mes = {
    8651974: 13,
    8651925: 13,
    8651920: 13,
    8651894: 13,
    8651695: 13,
    8651562: 13,
    8651493: 13,
    8651458: 13,
    8647972: 13,
    8647704: 13,
    8646708: 11,
    8644753: 10,
    8644620: 10,
    8644378: 10,
    8634961: 6,
    8628999: 2,
}
fe_ids = []
for cc in contracheques:
    contra = ContraCheque.objects.get(pk=cc)
    for ev in cc_evento[cc]:
        fe_change = contra.lancamentos.filter(
            evento__numero=ev, reference_month=cc_mes[cc]
        ).last()
        fe_ids.append(fe_change.pk)
FolhaEvento.objects.filter(pk__in=fe_ids, cid=None).update(cid=1)

FolhaEvento.objects.filter(cid=None).update(cid=0)
