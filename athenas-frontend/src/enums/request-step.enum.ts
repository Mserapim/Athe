export enum RequestStepEnum {
    APROVADOR = 1,
    DG = 2,
    RECESSO_FORENSE = 3,
    ASSESSORIA_DA_CORREGEDORIA = 4,
    CORREGEDORIA = 5,
    PGJ = 6,
    DGP = 7,
    ASSESSORIA_JURIDICA_1 = 10,
    DG_PROGRESSAO = 11,
    ASSESSORIA_JURIDICA_2 = 12,
    GERENCIA_DESENVOLVIMENTO = 13,
}

export function requestStepLabel(requestStep: RequestStepEnum) {
    if (requestStep == 1) return 'Aprovador';
    if (requestStep == 2) return 'DG';
    if (requestStep == 3) return 'Assessoria da Corregedoria';
    if (requestStep == 4) return 'Corregedoria';
    if (requestStep == 5) return 'PGJ';
    if (requestStep == 7) return 'DGP';
    if (requestStep == 10) return 'Assessoria Juridica (1º)';
    if (requestStep == 11) return 'DG - Progressão';
    if (requestStep == 12) return 'Assessoria Juridica (1º)';
    if (requestStep == 13) return 'Gerência de Desenvolvimento';
}
