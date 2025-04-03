import { Component, Inject } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackService } from '../request-new-electoral-slack.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE } from '@angular/material/core';
import { MAT_MOMENT_DATE_ADAPTER_OPTIONS, MomentDateAdapter } from '@angular/material-moment-adapter';
import { MY_FORMATS } from 'apps/app.component';
import moment from 'moment';

@Component({
    selector: 'request-new-electoral-slack-step2',
    templateUrl: './request-new-electoral-slack-step2.component.html',
    standalone: false,
    providers: [
        { provide: MAT_DATE_LOCALE, useValue: 'pt-BR' },
        {
            provide: DateAdapter,
            useClass: MomentDateAdapter,
            deps: [MAT_DATE_LOCALE, MAT_MOMENT_DATE_ADAPTER_OPTIONS],
            useFactory: (locale: string) => {
                const adapter = new MomentDateAdapter(locale);
                adapter.setLocale('pt-BR');
                return adapter;
            },
        },
        { provide: MAT_DATE_FORMATS, useValue: MY_FORMATS },
    ],
})
export class RequestNewElectoralSlackStep2Component {
    constructor(
        stepper: RequestStepperService,
        protected router: Router,
        protected service: RequestNewElectoralSlackService
    ) {
        stepper.currentStep = 1;
    }

    goBack() {
        moment.locale('pt-BR');
        this.router.navigate([
            `vdf/solicitacoes/novo/${this.service.path}`,
            'step1',
        ]);
    }

    async goNext() {
        try {
            this.service.message = '';
            if (this.service.hasStep3) return this.goStep3();

            await this.service.confirm();
            this.router.navigate(['vdf/solicitacoes']);
        } catch (e) {
            this.service.message = e?.response?.data?.message;
            console.log(e);
        }
    }

    goStep3() {
        this.router.navigate([
            `vdf/solicitacoes/novo/${this.service.path}`,
            'step3',
        ]);
    }

    get temVenda(): boolean {
        return this.service.items.some(item => item.type === 'VENDA');
    }

    get temUsufruto(): boolean {
        return this.service.items.some(item => item.type === 'USUFRUTO');
    }
}
