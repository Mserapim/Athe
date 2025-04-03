import { Component } from '@angular/core';
import {
    FormBuilder,
    FormControl,
    FormGroup,
    Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperService } from '../vdf-solicitacao-teletrabalho-desbloqueio-criar-stepper/request-new-relatorio-teletrabalho-semestral-criar-stepper.service';
import { MatDialog } from '@angular/material/dialog';
import { apiRhPvfRequestsEnviosRelatorioSemestralTeletrabalhosService } from 'api/rh/api-rh-pvf-requests-envios-relatorio-semestral-teletrabalhos.service';
import { apiVdfSolicitacaoDesbloqueioTeletrabalhoCriar } from 'api/vdf/api-vdf-solicitacao-desbloqueio-teletrabalho-criar.service';
import { RequestStepperService } from 'apps/vdf/request/components/request-stepper/request-stepper.service';

const today = new Date();
const month = today.getMonth();
const year = today.getFullYear();

@Component({
    selector: 'vdf-solicitacao-teletrabalho-desbloqueio-criar-step2',
    templateUrl: './vdf-solicitacao-teletrabalho-desbloqueio-criar-step2.component.html',
    standalone: false
})
export class VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep2Component {
    protected title = 'Visualize os dados para envio';
    protected mensagem = '';

    form = new FormGroup({
        anexo: new FormControl<{ valor: number }>(null, []),
        observacao: new FormControl<string>('', [Validators.required]),
    });

    constructor(
        private router: Router,
        public dialog: MatDialog,
        private stepper: RequestStepperService
    ) {
        stepper.currentStep = 1;
    }

    async ngOnInit() {}

    goBack() {
        this.stepper.currentStep = 0;
        return this.router.navigate([
            `vdf/solicitacoes/novo/teletrabalho-desbloqueio`,
            'step1',
        ]);
    }

    goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }

    async goConfirmar() {
        try {
            const {} = await apiVdfSolicitacaoDesbloqueioTeletrabalhoCriar({
                observacao: this.form.value?.observacao,
                anexo_id: this.form.value?.anexo?.valor,
            });
            this.goRequests();
        } catch (e) {
            this.mensagem = e?.response?.data?.message;
        }
    }
}
