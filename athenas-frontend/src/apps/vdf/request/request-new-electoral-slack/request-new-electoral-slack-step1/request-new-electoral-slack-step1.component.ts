import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackService } from '../request-new-electoral-slack.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-electoral-slack-step1',
    templateUrl: './request-new-electoral-slack-step1.component.html',
    standalone: false
})
export class RequestNewElectoralSlackStep1Component {
    title = '';
    subtitle = '';
    displayedColumns = [
        'group_period_name',
        'start_date_acquisition',
        'end_date_acquisition',
        'balance_available',
        'saldo_venda',
    ];

    constructor(
        protected service: RequestNewElectoralSlackService,
        protected stepper: RequestStepperService,
        protected router: Router
    ) {
        stepper.currentStep = 0;
    }

    async ngOnInit() {
        await this.service.loadRights();
    }

    get isValid() {
        return this.service.hasBalance;
    }

    getTotalBalanceAvailable(): number {
        return this.service.rights.reduce((acc, item) => acc + item.balance_available, 0);
    }
    
    getTotalSaldoVenda(): number {
        return this.service.rights.reduce((acc, item) => acc + item.saldo_venda, 0);
    }

    goNext() {
        this.router.navigate([
            `vdf/solicitacoes/novo/${this.service.path}`,
            'step2',
        ]);
    }
}
