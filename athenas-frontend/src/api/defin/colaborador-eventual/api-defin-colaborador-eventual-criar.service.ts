import { usePost } from 'api/@base/use-post';
import { ColaboradorEventualModelReturn } from '../modelos/colcadorardor-eventual-model';

interface Payload {
    nome_social: string;
    data_nascimento: string;
    sexo: string;
    raca_cor: number;
    cpf: string;
    email: string;
    pais_nacionalidade: number;
    pais_naturalidade: number;
    categoria_esocial: number;
    cargo_eventual: number;
}


export async function apiDefinColaboradorEventualCriar(
    payload: Payload
) {
    const { data } = await usePost<ColaboradorEventualModelReturn>(
        'rh/defin/colaborador-eventual/criar/',
        payload
    );

    return data;
}
