import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiFolhaPontoJustificativas } from 'api/folha-ponto/api-folha-ponto-justificativas.service';
import { apiRhSevidorService } from 'api/rh/api-rh-servidor.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class VdfFolhaPontoJustificativasService extends MpmtListagem2Service {
    filtros = new FormGroup({
        tipo_filtro: new FormControl<'COMPETENCIA' | 'PERIODO'>(null, []),
        inicio: new FormControl<Date>(null, []),
        fim: new FormControl<Date>(null, []),
        ano: new FormControl<number>(null, []),
        mes: new FormControl<number>(null, []),
        servidor_id: new FormControl<number>(null, []),
    });

    servidorInfo: { 
        matricula: string,
        nome: string,
        lotacao: string 
    } | null = null;

    constructor() {
        super();
    }

    limparFiltros() {
        this.filtros.reset();
    }

    public async obterDados(filtros: any) {
        try {
            filtros.page = undefined;
            filtros.per_page = undefined;

            const tipo_filtro = filtros.tipo_filtro;
            const ehCompetencia = tipo_filtro == 'COMPETENCIA';
            const payload = {
                inicio: !ehCompetencia
                    ? filtros.inicio?.toISOString()?.substring(0, 10)
                    : undefined,
                fim: !ehCompetencia
                    ? filtros.fim?.toISOString()?.substring(0, 10)
                    : undefined,
                ano: ehCompetencia ? filtros.ano : undefined,
                mes: ehCompetencia ? filtros.mes : undefined,
                servidor_id: filtros.servidor_id,
            };
            const result = await apiFolhaPontoJustificativas(payload);
            return result;
        } catch (e) {
            console.log(e);
        }
    }

    public async obterServidorInfo(servidor_id: number) {
        try {
            const result = await apiRhSevidorService({
                id: servidor_id,
                tipo_dados_servidor: 'completo'
            });
            const servidor = result as any;

            this.servidorInfo = {
                matricula: servidor.matricula,
                nome: servidor.nome,
                lotacao: servidor.lotacao_display
            };
    
            return this.servidorInfo;

        } catch (e) {
            console.log(e);
            this.servidorInfo = null;
            return null;
        }
    }

    protected async obterFiltros() {
        return {
            ...this.filtros.value,
        };
    }

    protected get downloadCsvSincrono() {
        return false;
    }
}
