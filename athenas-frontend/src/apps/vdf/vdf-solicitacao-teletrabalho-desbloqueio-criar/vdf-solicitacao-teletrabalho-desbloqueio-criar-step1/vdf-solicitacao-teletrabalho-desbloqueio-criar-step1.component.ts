import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperService } from '../vdf-solicitacao-teletrabalho-desbloqueio-criar-stepper/request-new-relatorio-teletrabalho-semestral-criar-stepper.service';
import { printDate } from 'utils/print-date';
import {
    apiVdfInfosTeletrabalhoBloqueadoService,
    ApiVdfInfosTeletrabalhoBloqueadoServiceResponseItem,
} from 'api/vdf/api-vdf-infos-teletrabalho-bloqueado.service';

@Component({
    selector: 'vdf-solicitacao-teletrabalho-desbloqueio-criar-step1',
    templateUrl: 'vdf-solicitacao-teletrabalho-desbloqueio-criar-step1.component.html',
    standalone: false
})
export class VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep1Component {
    public title = 'Visualize os dados para envio';
    public subtitle =
        'Essa Etapa é para que tenha ciência dos servidores que estão sob sua responsabilidade no programa de teletrabalho';
    public dados: ApiVdfInfosTeletrabalhoBloqueadoServiceResponseItem[] = [];
    public mensagem: string;
    public isLoading: boolean = false;

    constructor(
        private stepper: VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperService,
        private router: Router
    ) {
        stepper.currentStep = 0;
    }

    async ngOnInit() {
        this.load();
    }

    protected async load() {
        const response = await apiVdfInfosTeletrabalhoBloqueadoService({});
        this.dados = response.results;
    }

    async goNext() {
        return this.router.navigate([
            `vdf/solicitacoes/novo/teletrabalho-desbloqueio/`,
            'step2',
        ]);
    }

    goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }

    printDate = printDate;
}
