export enum RequestStatusEnum {
    AGUARDANDO_CIENCIA_DO_SUBSTITUTO = 1,
    AGUARDANDO_APROVADOR = 2,
    AGUARDANDO_EFETIVACAO = 3,
    EFETIVADO = 4,
    INDEFERIDO = 5,
    CANCELADO_DGP = 6,
    CANCELADO_SOLICITANTE = 7,
    AGUARDANDO_ASSESSORIA_DA_CORREGEDORIA = 8,
    AGUARDANDO_ENVIO = 9,
}

export function requestStatusLabel(requestStatus: RequestStatusEnum) {
    if (requestStatus == RequestStatusEnum.AGUARDANDO_CIENCIA_DO_SUBSTITUTO)
        return 'Aguardando Ciência do Substituto';
    if (requestStatus == RequestStatusEnum.AGUARDANDO_APROVADOR)
        return 'Aguardando Aprovador';
    if (requestStatus == RequestStatusEnum.AGUARDANDO_EFETIVACAO)
        return 'Aguardando efetivação';
    if (requestStatus == RequestStatusEnum.EFETIVADO) return 'Efetivado';
    if (requestStatus == RequestStatusEnum.INDEFERIDO) return 'Indeferido';
    if (requestStatus == RequestStatusEnum.CANCELADO_DGP)
        return 'Cancelado DGP';
    if (requestStatus == RequestStatusEnum.CANCELADO_SOLICITANTE)
        return 'Cancelado Solicitante';
    if (
        requestStatus == RequestStatusEnum.AGUARDANDO_ASSESSORIA_DA_CORREGEDORIA
    )
        return 'Aguardando Assessoria da Corregedoria';
    if (requestStatus == RequestStatusEnum.AGUARDANDO_ENVIO)
        return 'Aguardando Envio';
    return 'Desconhecido';
}

export function canRequestCancel(requestStatus: RequestStatusEnum) {
    return [
        RequestStatusEnum.AGUARDANDO_CIENCIA_DO_SUBSTITUTO,
        RequestStatusEnum.AGUARDANDO_APROVADOR,
        RequestStatusEnum.AGUARDANDO_EFETIVACAO,
        RequestStatusEnum.AGUARDANDO_ASSESSORIA_DA_CORREGEDORIA,
        RequestStatusEnum.AGUARDANDO_ENVIO,
    ].includes(requestStatus);
}

export function canRequestContinue(requestStatus: RequestStatusEnum) {
    return [RequestStatusEnum.AGUARDANDO_ENVIO].includes(requestStatus);
}
