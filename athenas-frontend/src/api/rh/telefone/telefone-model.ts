export class TelefoneModelReturn {
    id: number;
    pessoa: number;
    orgao_geral: number;
    orgao_geral_display: string;
    
    tipo_telefone: number;
    tipo_telefone_display: string;
    numero: string;
    publico: boolean;
    principal: boolean;

    data_alteracao: Date;
    modified_at: Date;
    modified_by: number;
    modified_by_display: string;
    created_at: Date;
    created_by: number;
    created_by_display: string;
}