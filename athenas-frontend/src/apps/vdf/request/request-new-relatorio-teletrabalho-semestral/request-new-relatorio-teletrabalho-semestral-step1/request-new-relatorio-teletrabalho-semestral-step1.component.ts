import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { baseDatasourceFactory } from 'datasources/base.datasource.factory';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { pvfUsufructsAcquisitionPeriods } from 'services/pvf/usufructs-acquisition-periods.service';
import { RequestsDataSource } from '../../requests/requests.datasource';
import { PvfUsufructsAcquisitionPeriodsDataSource } from 'datasources/pvf/usufructs-acquisition-periods.service.datasource';
import { Router } from '@angular/router';
import { RequestNewRelatorioTeletrabalhoSemestralStepperComponent } from '../request-new-relatorio-teletrabalho-semestral-stepper/request-new-relatorio-teletrabalho-semestral-stepper.component';
import { RequestNewRelatorioTeletrabalhoSemestralStepperService } from '../request-new-relatorio-teletrabalho-semestral-stepper/request-new-relatorio-teletrabalho-semestral-stepper.service';
import { RequestNewElectoralSlackStep1Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component';
import { apiRhPvfRequestsSendingTeleworksService } from 'api/rh/api-rh-pvf-requests-sending-teleworks.service';
import { apiRhPvfConfigEmployeesTeleworksStatus } from 'api/rh/api-rh-pvf-config-employees-teleworks-status.service';
import { apiRhPvfRequestsId } from 'api/rh/api-rh-pvf-requests-id.service';
import { RequestStatusEnum, canRequestCancel } from 'enums/request-status.enum';
import { requestStatusLabel } from 'enums/request-status.enum';
import { apiRhPvfConfigRequestsTimesheetsReferences } from 'api/rh/api-rh-pvf-config-requests-timesheets-references.service';
import { apiRhPvfConfigEmployeesTimesheetStatus } from 'api/rh/api-rh-pvf-config-employees-timesheet-status.service';
import { apiRhPvfRequestsSendingTimesheetsService } from 'api/rh/api-rh-pvf-requests-sending-timesheets.service';
import { apiReportRhPvfPointSheetService } from 'api/report/api-report-rh-pvf-point-sheet';
import { useDownload } from 'api/@base/use-download';
import { apiRhPvfRequestsIdCancelService } from 'api/rh/api-rh-pvf-requests-id-cancel.service';
import { RequestNewRelatorioTeletrabalhoSemestralService } from '../request-new-relatorio-teletrabalho-semestral.service';
import {
    ApiRhPvfRequestsSendingRelatorioSemestralTeletrabalhoItem,
    apiRhPvfRequestsListaRelatorioSemestralteletrabalhos,
} from 'api/rh/api-rh-pvf-requests-lista-relatorio-semestral-teletrabalhos.service';
import { printDate } from 'utils/print-date';

@Component({
    selector: 'request-new-relatorio-teletrabalho-semestral-step1',
    templateUrl: 'request-new-relatorio-teletrabalho-semestral-step1.component.html',
    standalone: false
})
export class RequestNewRelatorioTeletrabalhoSemestralStep1Component {
    public title = 'Visualize os dados para envio';
    public subtitle =
        'Essa Etapa é para que tenha ciência dos servidores que estão sob sua responsabilidade no programa de teletrabalho';

    public lista: ApiRhPvfRequestsSendingRelatorioSemestralTeletrabalhoItem[] =
        [];
    public mensagem: string;

    public isLoading: boolean = false;

    constructor(
        stepper: RequestNewRelatorioTeletrabalhoSemestralStepperService,
        private router: Router
    ) {
        stepper.currentStep = 1;
    }

    async ngOnInit() {
        this.load();
    }

    protected async load() {
        const response =
            await apiRhPvfRequestsListaRelatorioSemestralteletrabalhos({});
        this.lista = response.results;
    }

    public listaFiltradaAto1058() {
        return (
            this.lista.find((x) => x.tipo_ato.trim() == 'ATO 862/2019')
                ?.dados || []
        );
    }

    listaFiltradaAto1159() {}

    listaFiltradaAto862() {}

    async goNext() {
        return this.router.navigate([
            `vdf/solicitacoes/novo/relatorio-teletrabalho-semestral`,
            'step2',
        ]);
    }

    goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }

    printDate = printDate;
}
