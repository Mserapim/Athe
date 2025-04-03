export enum RequestTypeEnum {
    FERIAS_REGULAMENTARES = 1,
    FERIAS_INDIVIDUAIS = 2,
    RECESSO_FORENSE = 3,
    FOLGA_DE_ANIVERSARIO = 4,
    FOLGA_ELEITORAL = 5,
    PLANTAO_SERVIDORES = 6,
    FOLGA_COMPENSATORIAS_DE_MEMBROS = 7,
    PLANTAO_RECESSO_FORENSE_MEMBROS = 8,
    LICENCA_PREMIO = 9,
    RECESSO_ESTAGIARIOS = 10,
    CONCURSO_PROMOTOR_SUBSTITUTO = 11,
    CONCURSO_ESTAGIARIOS = 12,
    TRATAMENTO_SAUDE_15_DIAS = 13,
    TRATAMENTO_SAUDE_30_DIAS = 14,
    TRATAMENTO_SAUDE_JUNTA_MEDICA = 15,
    DOENCIA_PESSOA_DA_FAMILIA = 16,
    MATERNIDADE = 17,
    PATERNIDADE = 18,
    FALECIMENTO = 19,
    CASAMENTO = 20,
    ALTERACAO_DE_JORNADA = 21,
    CANCELAMENTO = 22,
    RETIFICACAO = 23,
    FOLHA_PONTO = 24,
    RELATORIO_TELETRABALHO = 25,
    SOLICITACAO_PLANTAO = 26, //Será substuido por CONFIRMACAO_DE_PLANTAO_SERVIDOR
    CONFIRMACAO_DE_PLANTAO_SERVIDOR = 26,
    AUSENCIA_DOACAO_SANGUE = 27,
    PROGRESSAO_VERTICAL = 28,
    PROGRESSAO_HORIZONTAL = 29,
    // DOACAO_SANGUE = 29,
    DOACAO_SANGUE2 = 30,
    TRATAMENTO_SAUDE_HORAS = 31,
    RECESSO_RESIDENTE = 32,
    EXERCICIO_CUMULATIVO = 33,
    CANCELAMENTO_TELETRABALHO = 34,
    RELATORIO_TELETRABALHO_SEMESTRAL = 35,
    SOLICITACAO_FOLGA = 36,
    DOENCIA_PESSOA_DA_FAMILIA_JUNTA_MEDICA = 37,
    SOLICITACAO_AUX_CRECHE_IR = 38,
    DESBLOQUEIO_DO_TELETRABALHO = 39,
    SOLICITACAO_CREDITO_DISPENSA_ELEITORAL = 40,
}

export function isRequestDesbloqueioTeletrabalho(requestType: RequestTypeEnum) {
    return [RequestTypeEnum.DESBLOQUEIO_DO_TELETRABALHO].includes(requestType);
}

export function isRequestRelatorioTeletrabalhoSemestral(
    requestType: RequestTypeEnum
) {
    return [RequestTypeEnum.RELATORIO_TELETRABALHO_SEMESTRAL].includes(
        requestType
    );
}

export function isRequestTypeProgressaoVertical(requestType: RequestTypeEnum) {
    return [RequestTypeEnum.PROGRESSAO_VERTICAL].includes(requestType);
}

export function isRequestTypeProgressaoHorizontal(
    requestType: RequestTypeEnum
) {
    return [RequestTypeEnum.PROGRESSAO_HORIZONTAL].includes(requestType);
}

export function isRequestTypeExecicioCumulativo(requestType: RequestTypeEnum) {
    return [RequestTypeEnum.EXERCICIO_CUMULATIVO].includes(requestType);
}

export function isRequestTypeDesbloquearTeletrabalho(
    requestType: RequestTypeEnum
) {
    return [RequestTypeEnum.EXERCICIO_CUMULATIVO].includes(requestType);
}

export function isRequestTypeRetificationUsufruct(
    requestType: RequestTypeEnum
) {
    return [RequestTypeEnum.RETIFICACAO].includes(requestType);
}

export function isRequestTypeTelework(requestType: RequestTypeEnum) {
    return [RequestTypeEnum.RELATORIO_TELETRABALHO].includes(requestType);
}

export function isRequestTypeTimesheet(requestType: RequestTypeEnum) {
    return [RequestTypeEnum.FOLHA_PONTO].includes(requestType);
}

export function isRequestTypeShiftServerConfirm(requestType: RequestTypeEnum) {
    return [RequestTypeEnum.CONFIRMACAO_DE_PLANTAO_SERVIDOR].includes(
        requestType
    );
}

export function isRequestTypeAbsence(requestType: RequestTypeEnum) {
    return [
        RequestTypeEnum.TRATAMENTO_SAUDE_15_DIAS,
        RequestTypeEnum.TRATAMENTO_SAUDE_30_DIAS,
        RequestTypeEnum.TRATAMENTO_SAUDE_HORAS,
        RequestTypeEnum.TRATAMENTO_SAUDE_JUNTA_MEDICA,
        RequestTypeEnum.DOENCIA_PESSOA_DA_FAMILIA,
        RequestTypeEnum.DOENCIA_PESSOA_DA_FAMILIA_JUNTA_MEDICA,
        RequestTypeEnum.MATERNIDADE,
        RequestTypeEnum.PATERNIDADE,
        RequestTypeEnum.FALECIMENTO,
        RequestTypeEnum.CASAMENTO,
        // RequestType.DOACAO_SANGUE,
        RequestTypeEnum.AUSENCIA_DOACAO_SANGUE,
    ].includes(requestType);
}

export function isRequestTypeUsufruct(requestType: RequestTypeEnum) {
    return [
        RequestTypeEnum.FERIAS_REGULAMENTARES,
        RequestTypeEnum.FERIAS_INDIVIDUAIS,
        RequestTypeEnum.RECESSO_FORENSE,
        RequestTypeEnum.FOLGA_DE_ANIVERSARIO,
        RequestTypeEnum.FOLGA_ELEITORAL,
        RequestTypeEnum.PLANTAO_SERVIDORES,
        RequestTypeEnum.FOLGA_COMPENSATORIAS_DE_MEMBROS,
        RequestTypeEnum.PLANTAO_RECESSO_FORENSE_MEMBROS,
        RequestTypeEnum.LICENCA_PREMIO,
        RequestTypeEnum.RECESSO_ESTAGIARIOS,
        RequestTypeEnum.RECESSO_RESIDENTE,
        RequestTypeEnum.CONCURSO_PROMOTOR_SUBSTITUTO,
        RequestTypeEnum.CONCURSO_ESTAGIARIOS,
        // RequestType.DOACAO_SANGUE,
        RequestTypeEnum.DOACAO_SANGUE2,

    ].includes(requestType);
}

export function isRequestTipoCancelamentoTeletrabalho(
    requestType: RequestTypeEnum
) {
    return [RequestTypeEnum.CANCELAMENTO_TELETRABALHO].includes(requestType);
}

export function isRequestTipoSolicitacaoCreditoFolga(
    requestType: RequestTypeEnum
) {
    return [RequestTypeEnum.SOLICITACAO_FOLGA].includes(requestType);
}

export function isRequestTipoSolicitacaoAuxilioCrecheIr(
    requestType: RequestTypeEnum
) {
    return [RequestTypeEnum.SOLICITACAO_AUX_CRECHE_IR].includes(requestType);
}

export function isRequestTypeCancel(requestStatus: RequestTypeEnum) {
    return requestStatus == RequestTypeEnum.CANCELAMENTO;
}

export function isRequestSolicitacaoCreditoDispensaEleitoral(requestStatus: RequestTypeEnum) {
    return requestStatus == RequestTypeEnum.SOLICITACAO_CREDITO_DISPENSA_ELEITORAL;
}

export function requestTypeLabel(requestStatus: RequestTypeEnum) {
    // if (requestStatus == RequestStatus.AGUARDANDO_CIENCIA_DO_SUBSTITUTO)
    //     return 'Aguardando Ciência do Substituto';
    // if (requestStatus == RequestStatus.AGUARDANDO_APROVADOR)
    //     return 'Aguardando Aprovador';
    // if (requestStatus == RequestStatus.AGUARDANDO_EFETIVACAO)
    //     return 'Aguardando efetivação';
    // if (requestStatus == RequestStatus.EFETIVADO) return 'Efetivado';
    // if (requestStatus == RequestStatus.INDEFERIDO) return 'Indeferido';
    // if (requestStatus == RequestStatus.CANCELADO_DGP) return 'Cancelado DGP';
    // if (requestStatus == RequestStatus.CANCELADO_SOLICITANTE)
    //     return 'Cancelado Solicitante';
    // if (requestStatus == RequestStatus.AGUARDANDO_ASSESSORIA_DA_CORREGEDORIA)
    //     return 'Aguardando Assessoria da Corregedoria';
    // if (requestStatus == RequestStatus.AGUARDANDO_ENVIO)
    //     return 'Aguardando Envio';
    // return 'Desconhecido';
}
