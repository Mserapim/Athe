import { usePost } from 'api/@base/use-post';

export interface Payload {
    veiculo?: {
        placa: string;
        kilometragem?: string;
        marca: string;
        modelo: string;
        renavam?: string;
        capacidade_passageiros: number;
    };
    motorista?: {
        motorista: number;
        conta_bancaria_pgto: number;
    };
    destinos: {
        ids: number[];
        dataHora: string;
    }[];
}

export async function apiVeiculoMotoristaDaaCriar(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/analise-daa-veiculo-passageiros/criar/',
        payload
    );
    return data.data;
}
