import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDefinColaboradoresEventuais } from 'api/defin/colaborador-eventual/api-defin-colaboradores-eventuais.service';
import { MpmtPaginaListagemAcao, MpmtPaginaListagemColuna } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.interface';
import { MpmtPaginaListagemService } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.service';

@Injectable()
export class ColaboradorEventualService extends MpmtPaginaListagemService {

    irEditar: ((linha:any) => void) | undefined;

    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
    });

    constructor() {
        super();
        this.filtros.valueChanges.subscribe(() => this.recarregarUmaVez())
    }

    public async obterDados(filtros: any) {
        return apiDefinColaboradoresEventuais(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }


    protected async obterColunas() {
        return <MpmtPaginaListagemColuna[]>[
            {
                codigo: 'id',
                titulo: 'Codigo',
                visivel: false,
            },
            {
                codigo: 'status',
                titulo: 'Status',
                visivel: true,
                tipo: 'BOLEANO_ICONE',
            },
            {
                codigo: 'nome_social',
                titulo: 'Nome',
                visivel: true,
            },
            {
                codigo: 'data_nascimento',
                titulo: 'Data Nascimento',
                visivel: true,
                tipo: 'DATA'
            },
            {
                codigo: 'sexo_display',
                titulo: 'Sexo',
                visivel: true,
            },
            {
                codigo: 'raca_cor_display',
                titulo: 'Raça/Etnia',
                visivel: true,
            },
            {
                codigo: 'cpf',
                titulo: 'CPF',
                visivel: true,
            },
            {
                codigo: 'email',
                titulo: 'Email',
                visivel: true,
            },
            {
                codigo: 'created_at',
                titulo: 'Criado em',
                visivel: false,
                tipo: 'DATA'
            },
            {
                codigo: 'created_by_display',
                titulo: 'Criado por',
                visivel: false,
            },
            {
                codigo: 'modified_at',
                titulo: 'Modificado em',
                visivel: false,
                tipo: 'DATA'
            },
            {
                codigo: 'modified_by_display',
                titulo: 'Modificado por',
                visivel: false,
            },
        ]
    }

    protected async obterAcoes(): Promise<MpmtPaginaListagemAcao[]> {
        return [
            {
                titulo: 'Editar',
                icone: 'edit',
                requerPermissao: 'editar',
                aoClicar: (linha: any) => this.irEditar(linha),
            },
        ]
    }


}