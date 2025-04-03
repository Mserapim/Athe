import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';


import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import { apiDiariasPrestacoesContas } from 'api/diarias/prestacao-contas/api-diarias-prestacoes-contas.service';
import { apiDiariasPerfilAprovador } from 'api/diarias/config/grupo-aprovador/api-perfil-aprovador';

@Injectable()
export class PrestacoesContasService extends MpmtListagem2Service {

    status_prestacao = [
        { id: 'entregue', descricao: 'Entregue' },
        { id: 'em_analise', descricao: 'Em Análise' },
        { id: 'aguardando', descricao: 'Aguardando' },
        { id: 'atrasado', descricao: 'Atrasado' },
        { id: 'com_pendencias', descricao: 'Com Pendências' },
        { id: 'aprovado', descricao: 'Aprovado' },
    ];

    perfil: any = null;

    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        status: new FormControl<any[]>([this.status_prestacao[0]], []),
        servidores: new FormControl<any[]>(null, []),

    });

    constructor() {
        super();
        this.filtros.valueChanges.subscribe(()=>this.recarregarListagem())
    }

    public async obterDados(filtros: any) {
        return apiDiariasPrestacoesContas(filtros);
    }

    protected async obterFiltros() {
        const servidores_valor = this.filtros.get('servidores')?.value;
        let servidores = null;
        if (servidores_valor){
            servidores = servidores_valor.map(servidor => servidor.pk);
        }
        const status_value = this.filtros.get('status')?.value;
        let status = null;
        if (status_value){
            status = status_value.map(status => status.id);
        }

        return { ...this.filtros.value , servidores:servidores, status:status};
    }

    public async carregarPerfilAprovador(id: number) {
            try {
                this.perfil = (await apiDiariasPerfilAprovador({id:id}));
            } catch (error) {
                console.error('Erro ao carregar os dados do perfil de aprovador do usuário logado :', error);
            }
    
        }

    
}
