import { Modulo } from './modulo';

export class Menu {
    id: number;
    pk: number;
    nome: string;
    acoes: string[];
    ordem: number;
    icone?: string;
    situacao: 'ATIVO';
    url: string;
    favorito?: boolean;
    modulo?: Modulo;
    descricao?: string;
}
