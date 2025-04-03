import { PagamentoModelReturn } from "./pagamento-model";

export class ColaboradorEventualModelReturn {
    id:number;
    nome_social: string;
    data_nascimento: Date;
    sexo: string;
    sexo_display: string;
    raca_cor: number;
    raca_cor_display: string;
    cpf: string;
    email: string;
    status: boolean;
    pais_nacionalidade: number;
    pais_nacionalidade_display: string;
    pais_naturalidade: number;
    pais_naturalidade_display: string;
    categoria_esocial: number
    categoria_esocial_display: string;
    cargo_eventual: number;
    cargo_eventual_display: string;

    pagamentos: PagamentoModelReturn[];
    enderecos: any[];
    telefones: any[];
    modified_at: Date;
    modified_by: number;
    modified_by_display: string;
    created_at: Date;
    created_by: number;
    created_by_display: string;
}
