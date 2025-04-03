import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';

export interface Payload extends ListPayload {
    keyword?: string;
}

export class ApiGestaoVdfResponseItem {
    id: number;
    tipo_solicitacao: string;
    mes_referencia:  null;
    situacao: string;
    servidor: string;
    aprovador: string;
    dias_aguardando_aprovacao:  number;
    periodo_aquisitivo:  null;
    historico:  {
        acao: string;
        grupo: string;
        servidor: string;
        data: string;
        observacao:  null
    }[]
}

class Response extends ListPaginated<ApiGestaoVdfResponseItem> {}

export async function apiGestaoVdf(payload: Payload) {
    // const { data } = await useGet<Response>('/athenas/api/v2/vdf/gestao', payload);
    // return data;
    return MOCK
}

const MOCK = {
    "total": 286610,
    "page": 1,
    "per_page": 5,
    "navigation": {
        "next": "http://10.2.5.199:8000/athenas/api/v2/vdf/gestao?page=2&per_page=5",
        "previous": null
    },
    "results": [
        {
            "id": 82869,
            "tipo_solicitacao": "Ausência",
            "mes_referencia": null,
            "situacao": "Aguardando Aprovador",
            "servidor": "541:SIMONE REZENDE SANTANA",
            "aprovador": "CAIO MARCIO LOUREIRO",
            "dias_aguardando_aprovacao": 43,
            "periodo_aquisitivo": null,
            "historico": [
                {
                    "acao": "Solicitação",
                    "grupo": "",
                    "servidor": "SIMONE REZENDE SANTANA",
                    "data": "2024-12-11T14:59:41.742548",
                    "observacao": null
                },
                {
                    "acao": "Solicitação",
                    "grupo": "",
                    "servidor": "SIMONE REZENDE SANTANA",
                    "data": "2024-12-11T14:59:41.742548",
                    "observacao": null
                },
                {
                    "acao": "Solicitação",
                    "grupo": "",
                    "servidor": "SIMONE REZENDE SANTANA",
                    "data": "2024-12-11T14:59:41.742548",
                    "observacao": null
                }
            ]
        },
        {
            "id": 82868,
            "tipo_solicitacao": "Folha Ponto",
            "mes_referencia": "11/2024",
            "situacao": "Aguardando Aprovador",
            "servidor": "7913:GIOVANA BARBARA NEVES LOURENCO",
            "aprovador": "JORGE PAULO DAMANTE PEREIRA",
            "dias_aguardando_aprovacao": 43,
            "periodo_aquisitivo": null,
            "historico": [
                {
                    "acao": "Abrir Solicitação",
                    "grupo": "",
                    "servidor": "GIOVANA BARBARA NEVES LOURENCO",
                    "data": "2024-12-11T14:57:49.850290",
                    "observacao": ""
                },
                {
                    "acao": "Solicitação",
                    "grupo": "",
                    "servidor": "GIOVANA BARBARA NEVES LOURENCO",
                    "data": "2024-12-11T14:58:35.836015",
                    "observacao": null
                }
            ]
        },
        {
            "id": 82868,
            "tipo_solicitacao": "Folha Ponto",
            "mes_referencia": "11/2024",
            "situacao": "Aguardando Aprovador",
            "servidor": "7913:GIOVANA BARBARA NEVES LOURENCO",
            "aprovador": "JORGE PAULO DAMANTE PEREIRA",
            "dias_aguardando_aprovacao": 43,
            "periodo_aquisitivo": null,
            "historico": [
                {
                    "acao": "Abrir Solicitação",
                    "grupo": "",
                    "servidor": "GIOVANA BARBARA NEVES LOURENCO",
                    "data": "2024-12-11T14:57:49.850290",
                    "observacao": ""
                },
                {
                    "acao": "Solicitação",
                    "grupo": "",
                    "servidor": "GIOVANA BARBARA NEVES LOURENCO",
                    "data": "2024-12-11T14:58:35.836015",
                    "observacao": null
                }
            ]
        },
        {
            "id": 82867,
            "tipo_solicitacao": "Folha Ponto",
            "mes_referencia": "12/2024",
            "situacao": "Aguardando Envio",
            "servidor": "11408:GABRIEL PINHEIRO DE SOUZA",
            "aprovador": "-",
            "dias_aguardando_aprovacao": 43,
            "periodo_aquisitivo": null,
            "historico": [
                {
                    "acao": "Abrir Solicitação",
                    "grupo": "",
                    "servidor": "GABRIEL PINHEIRO DE SOUZA",
                    "data": "2024-12-11T14:55:49.111432",
                    "observacao": ""
                }
            ]
        },
        {
            "id": 82866,
            "tipo_solicitacao": "Folha Ponto",
            "mes_referencia": "12/2024",
            "situacao": "Aguardando Envio",
            "servidor": "10465:PAULA DORNELLES MARTINS",
            "aprovador": "-",
            "dias_aguardando_aprovacao": 43,
            "periodo_aquisitivo": null,
            "historico": [
                {
                    "acao": "Abrir Solicitação",
                    "grupo": "",
                    "servidor": "PAULA DORNELLES MARTINS",
                    "data": "2024-12-11T14:55:22.791591",
                    "observacao": ""
                }
            ]
        }
    ]
}