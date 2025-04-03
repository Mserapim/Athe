import { Component, Input, OnChanges } from '@angular/core';
import { Router } from '@angular/router';
import {
    ApiVdfRequestsSendingTeleworksAfastamentosItem,
    apiVdfRequestsSendingTeleworksAfastamentos,
} from 'api/vdf/api-vdf-requests-sending-teleworks-afastamentos.service';

@Component({
    selector: 'request-show-telework-afastamentos',
    templateUrl: './request-show-telework-afastamentos.component.html',
    standalone: false
})
export class RequestShowTeleworkAfastamentosComponent implements OnChanges {
    @Input() servidorId!: number;
    @Input() reference!: string;

    displayedColumns = ['tipo', 'data_inicio', 'data_fim'];

    public results: ApiVdfRequestsSendingTeleworksAfastamentosItem[] = null;

    constructor(protected router: Router) {}

    async ngOnChanges() {
        if (!this.servidorId) return;
        if (!this.reference) return;
        await this.loadAfastamentos();
    }

    public async loadAfastamentos() {
        const [mes, ano] = this.reference.split('/').map((x) => +x);
        const { results } = await apiVdfRequestsSendingTeleworksAfastamentos({
            ano: ano,
            mes: mes,
            servidor_id: this.servidorId,
        });
        this.results = results;
    }

    get carregado() {
        return this.results;
    }
}
