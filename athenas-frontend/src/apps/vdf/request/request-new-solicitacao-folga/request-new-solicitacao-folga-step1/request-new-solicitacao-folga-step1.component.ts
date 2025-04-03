import { Component } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { RequestNewSolicitacaoFolgaService } from '../request-new-solicitacao-folga.service';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { addDay } from 'utils/add-day';
import {
    ApiVdfConfigTipoFolgaServiceResponseItem,
    apiVdfConfigTipoFolgaService,
} from 'api/vdf/api-vdf-config-tipos-folgas.service';
import { ApiVdfSolicitacaoFolgaPayload } from 'api/vdf/api-vdf-solicitacao-folga-criar.service';

@Component({
    selector: 'request-new-solicitacao-folga-step1',
    templateUrl: './request-new-solicitacao-folga-step1.component.html',
    standalone: false
})
export class RequestSolicitacaoFolgaStep1Component {
    arquivo = null;
    arquivoId: number = null;
    message: string;

    tipos: ApiVdfConfigTipoFolgaServiceResponseItem[] = [];

    protected form = new FormGroup({
        arquivo: new FormControl<File | null>(null, []),
        arquivoId: new FormControl<number | null>(null, [Validators.required]),
        dataInicio: new FormControl<Date | null>(null, [Validators.required]),
        dias: new FormControl<number>(1, [Validators.required]),
        dataFim: new FormControl<Date | null>(null, []),
        observacao: new FormControl<string>('', []),
        tipoItem: new FormControl<ApiVdfConfigTipoFolgaServiceResponseItem>(
            undefined,
            []
        ),
    });

    constructor(
        protected router: Router,
        protected requestNewSolicitacaoFolgaService: RequestNewSolicitacaoFolgaService
    ) {}

    async loadTipos($event?) {
        const { results } = await apiVdfConfigTipoFolgaService({
            per_page: 30,
            keyword: $event?.target?.value,
        });
        this.tipos = results;
    }

    displayFn(item: ApiVdfConfigTipoFolgaServiceResponseItem): string {
        return item && item.label ? item.label : '';
    }

    async incluirArquivo($arquivo) {
        this.arquivo = $arquivo.target.files[0];
        const response = await gedUpload({
            file: this.arquivo,
            fileName: this.arquivo.name,
        });

        this.form.value.arquivo = $arquivo.target.files[0];
        this.form.value.arquivoId = response.data.file_id;
        this.arquivoId = response.data.file_id;
        this.form.patchValue({
            arquivoId: response.data.file_id,
        });
    }

    public getPayload() {
        return <ApiVdfSolicitacaoFolgaPayload>{
            anexo: this.form.value.arquivoId,
            tipo_folga: this.form.value.tipoItem?.value,
            data_inicio: this.form.value.dataInicio,
            data_fim: this.form.value.dataFim,
            observation: this.form.value.observacao,
        };
    }

    async goConfirm() {
        this.message = '';
        try {
            this.requestNewSolicitacaoFolgaService.payload = this.getPayload();
            const response =
                await this.requestNewSolicitacaoFolgaService.confirm();
            if (response) this.router.navigate(['vdf/solicitacoes']);
        } catch (e) {
            this.message = e.response?.data?.message;
        }
    }

    alterarDias($event) {
        this.form.value.dias = $event;
        if (!this.form.value.dataInicio || !this.form.value.dias) return;
        this.form.value.dataFim = addDay(
            this.form.value.dataInicio,
            this.form.value.dias - 1
        );
    }

    alterarDataInicio($event) {
        this.form.value.dataInicio = $event;
        if (!this.form.value.dataInicio) return;
        if (!this.form.value.dias) return;
        this.form.value.dataFim = addDay(
            this.form.value.dataInicio,
            this.form.value.dias - 1
        );
    }
}
