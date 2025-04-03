import { Grupo } from './grupo';

export class Modulo {
    pk?: number;
    nome: string;
    codigo: string;
    sigla: string;
    icone?: string;
    path?: string;
    grupos?: Grupo[];
}
