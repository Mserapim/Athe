import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasMinhasDiarias } from 'api/diarias/api-diarias-minhas-diarias.service'; 
import { apiDiariasChoicesFinalidades } from 'api/diarias/choices/api-diarias-finalidades.service';
import { apiDiariasChoicesSituacoes } from 'api/diarias/choices/api-diarias-situacoes.service';
import { apiDiariasChoicesMotivosViagem } from 'api/diarias/choices/api-diarias-motivos-viagem.service';

import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import { apiAuthCurrentUserService, AuthCurrentUserResponse } from 'api/auth/api-auth-current-user.service';
import { apiDiariasConfigFluxo } from 'api/diarias/config/api-diarias-config-fluxo.service';

@Injectable()
export class MinhasDiariasService extends MpmtListagem2Service {
    situacoes: { descricao: string; id: number }[] = [];
    motivos_viagem: { descricao: string; id: number }[] = [];
    finalidades: { descricao: string; id: number }[] = [];

    currentUser: AuthCurrentUserResponse;

    loading = false;

    urlAjuda: string | null = null;
    
    tipos_viagem = [
        { id: 'ESTADUAL', descricao: 'Estadual' },
        { id: 'NACIONAL', descricao: 'Nacional' },
        { id: 'INTERNACIONAL', descricao: 'Internacional' },
    ];

    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        situacoes: new FormControl<number[]>(null, []),
        tipos_viagem: new FormControl<string[]>(null, []),
        motivos_viagem: new FormControl<number[]>(null, []),
        finalidades: new FormControl<number[]>(null, []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        this.loading = true;
        const dados = apiDiariasMinhasDiarias(filtros);
        this.loading = false;
        return dados
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }

    public async carregarSituacoes() {
        try {
            this.situacoes = (await apiDiariasChoicesSituacoes({})).results;
        } catch (error) {
            console.error('Erro ao carregar os tipos de Situações da solicitação:', error);
        }
    }

    public async carregarMotivosViagem() {
        try {
            this.motivos_viagem = (await apiDiariasChoicesMotivosViagem({})).results;
        } catch (error) {
            console.error('Erro ao carregar os motivos de Viagem:', error);
        }
    }

    public async carregarFinalidades() {
        try {
            this.finalidades = (await apiDiariasChoicesFinalidades({})).results;
        } catch (error) {
            console.error('Erro ao carregar as finalidades de viagem:', error);
        }
    }

    public async carregarUsuarioAtual() {
        try {
            this.currentUser = await apiAuthCurrentUserService({});
        } catch (error) {
            console.error('Erro ao carregar dados do usuário atual:', error);
        }
        return this.currentUser
    }

    public async carregarLinkAjuda() {
        const fluxoRascunho = 2 
        try {
            const configFluxo = await apiDiariasConfigFluxo({ id: fluxoRascunho });
            this.urlAjuda = configFluxo?.link_informacao || null;
        } catch (error) {
            console.error('Erro ao carregar o link de ajuda:', error);
            this.urlAjuda = null;
        }
    }
}
