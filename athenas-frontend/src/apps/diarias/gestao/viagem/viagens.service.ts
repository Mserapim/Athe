import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasChoicesFinalidades } from 'api/diarias/choices/api-diarias-finalidades.service';
import { apiDiariasChoicesSituacoes } from 'api/diarias/choices/api-diarias-situacoes.service';
import { apiDiariasChoicesMotivosViagem } from 'api/diarias/choices/api-diarias-motivos-viagem.service';

import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import { apiDiariasViagens } from 'api/diarias/api-diarias-viagens.service';
import { apiDiariasChoicesEtapas } from 'api/diarias/choices/api-diarias-etapas.service';
import { apiDiariasPerfilAprovador } from 'api/diarias/config/grupo-aprovador/api-perfil-aprovador';
import { VerDiariaService } from './ver-diaria-aprovador/ver-diaria-aprovador.service';

@Injectable()
export class ViagensService extends MpmtListagem2Service {
    situacoes: { descricao: string; id: number }[] = [];
    etapas: { descricao: string; id: number }[] = [];
    motivos_viagem: { descricao: string; id: number }[] = [];
    finalidades: { descricao: string; id: number }[] = [];

    perfil: any = null;

    tipos_viagem = [
        { id: 'ESTADUAL', descricao: 'Estadual' },
        { id: 'NACIONAL', descricao: 'Nacional' },
        { id: 'INTERNACIONAL', descricao: 'Internacional' },
    ];

    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        situacoes: new FormControl<number[]>(null, []),
        etapas: new FormControl<any[]>(null, []),
        tipos_viagem: new FormControl<any[]>(null, []),
        motivos_viagem: new FormControl<any[]>(null, []),
        finalidades: new FormControl<any[]>(null, []),
        servidores: new FormControl<any[]>(null, []),
    });

    constructor(
        private verDiariaService: VerDiariaService,
    ) {
        super();
        this.filtros.valueChanges.subscribe(()=>this.recarregarListagem())
    }

    public async carregarPerfilAprovador(id: number) {
        try {
            this.perfil = (await apiDiariasPerfilAprovador({id:id}));
            this.verDiariaService.etapasAprovador = this.perfil.etapas_aprovador;
        } catch (error) {
            console.error('Erro ao carregar os dados do perfil de aprovador do usuário logado :', error);
        }
        
        const etapas = this.perfil.etapas_aprovador_obj.map(etapa => ({ id: etapa.value, descricao: etapa.label }));

        this.filtros.get('etapas')?.setValue(etapas);
    }

    public async obterDados(filtros: any) {
        return apiDiariasViagens(filtros);
    }

    protected async obterFiltros() {
        const etapas_valor = this.filtros.get('etapas')?.value;
        let etapas = null;
        if (etapas_valor){
            etapas = etapas_valor.map(etapa => etapa.id);
        }

        const tipos_viagem_valor = this.filtros.get('tipos_viagem')?.value;
        let tipos_viagem = null;
        if (tipos_viagem_valor){
            tipos_viagem = tipos_viagem_valor.map(tipo => tipo.id);
        }


        const motivos_viagem_valor = this.filtros.get('motivos_viagem')?.value;
        let motivos_viagem = null;
        if (motivos_viagem_valor){
            motivos_viagem = motivos_viagem_valor.map(motivo => motivo.id);
        }

        const finalidades_valor = this.filtros.get('finalidades')?.value;
        let finalidades = null;
        if (finalidades_valor){
            finalidades = finalidades_valor.map(finalidade => finalidade.id);
        }

        const servidores_valor = this.filtros.get('servidores')?.value;
        let servidores = null;
        if (servidores_valor){
            servidores = servidores_valor.map(servidor => servidor.pk);
        }

        return { ...this.filtros.value, etapas:etapas, tipos_viagem:tipos_viagem, motivos_viagem:motivos_viagem, finalidades:finalidades, servidores: servidores };
    }

    
}
