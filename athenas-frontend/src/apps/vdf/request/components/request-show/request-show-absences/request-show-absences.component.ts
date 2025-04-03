import { Component, Inject, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { useGedDownload } from 'api/@base/use-ged-download';
import { printDate } from 'utils/print-date';
import { apiGedDownload } from 'api/ged/api-ged-download.service';
import { apiRhPvfRequestsAbsencesBloodDonationId } from 'api/rh/api-rh-pvf-requests-absences-blood-donation-id.service';
import { apiRhPvfRequestsAbsencesHealthFamilyLicensesId } from 'api/rh/api-rh-pvf-requests-absences-health-family-licenses-id.service';
import { apiRhPvfRequestsAbsencesHealthLicensesId } from 'api/rh/api-rh-pvf-requests-absences-health-licenses-id.service';
import { apiRhPvfRequestsAbsencesMarriageAbsencesId } from 'api/rh/api-rh-pvf-requests-absences-marriage-absences-id.service';
import { apiRhPvfRequestsAbsencesMaternityAbsencesId } from 'api/rh/api-rh-pvf-requests-absences-maternity-absences-id.service';
import { apiRhPvfRequestsAbsencesMaternityAbsencesService } from 'api/rh/api-rh-pvf-requests-absences-maternity-absences.service';
import { apiRhPvfRequestsAbsencesMourningAbsencesId } from 'api/rh/api-rh-pvf-requests-absences-mourning-absences-id.service';
import { apiRhPvfRequestsAbsencesPaternityAbsencesId } from 'api/rh/api-rh-pvf-requests-absences-paternity-absences-id.service';
import { ApiRhPvfRequestsIdUsufructsResponseItem } from 'api/rh/api-rh-pvf-requests-id-usufructs.service';
import { RequestTypeEnum } from 'enums/request-type.enum';
import {SelectItem} from "../../../../../../utils/select-item";
@Component({
    selector: 'request-show-absences',
    templateUrl: './request-show-absences.component.html',
    standalone: false
})
export class RequestShowAbsencesComponent implements OnInit {
    @Input() requestId!: number;
    @Input() portalRequestType!: number;

    //classificacoes : SelectItem[] = [{label: 'Normal', value: 1}, {label: 'Antecipação', value: 2}]
    classificacoes : SelectItem[] = [{label: 'Normal', value: 1}]


    public data: any = {};

    constructor(private route: ActivatedRoute, protected router: Router) {}

    ngOnInit() {
        // this.load({ requestId: this.requestId! });
    }

    printDate = printDate;

    async ngOnChanges() {
        console.log('ngOnChanges');
        try {
            const response = await this.getService()({
                requestId: this.requestId,
            });
            this.data = response;
        } catch (e) {
            console.log(e);
        }
    }

    getService() {
        if (
            this.portalRequestType == RequestTypeEnum.TRATAMENTO_SAUDE_15_DIAS
        ) {
            return apiRhPvfRequestsAbsencesHealthLicensesId;
        }

        if (
            this.portalRequestType == RequestTypeEnum.TRATAMENTO_SAUDE_30_DIAS
        ) {
            return apiRhPvfRequestsAbsencesHealthLicensesId;
        }

        if (
            this.portalRequestType ==
            RequestTypeEnum.TRATAMENTO_SAUDE_JUNTA_MEDICA
        ) {
            return apiRhPvfRequestsAbsencesHealthLicensesId;
        }

        if (this.portalRequestType == RequestTypeEnum.TRATAMENTO_SAUDE_HORAS) {
            return apiRhPvfRequestsAbsencesHealthLicensesId;
        }

        if (
            this.portalRequestType == RequestTypeEnum.DOENCIA_PESSOA_DA_FAMILIA ||
            this.portalRequestType == RequestTypeEnum.DOENCIA_PESSOA_DA_FAMILIA_JUNTA_MEDICA
        ) {
            return apiRhPvfRequestsAbsencesHealthFamilyLicensesId;
        }

        if (this.portalRequestType == RequestTypeEnum.FALECIMENTO) {
            return apiRhPvfRequestsAbsencesMourningAbsencesId;
        }

        if (this.portalRequestType == RequestTypeEnum.CASAMENTO) {
            return apiRhPvfRequestsAbsencesMarriageAbsencesId;
        }

        if (this.portalRequestType == RequestTypeEnum.PATERNIDADE) {
            return apiRhPvfRequestsAbsencesPaternityAbsencesId;
        }

        if (this.portalRequestType == RequestTypeEnum.MATERNIDADE) {
            return apiRhPvfRequestsAbsencesMaternityAbsencesId;
        }

        if (this.portalRequestType == RequestTypeEnum.AUSENCIA_DOACAO_SANGUE) {
            return apiRhPvfRequestsAbsencesBloodDonationId;
        }

        throw 'SERVICE_NOT_IMPLEMENTED';
    }

    // forceFileDownload(response, title) {
    //     console.log(title);
    //     const url = url(
    //         'local.mpmt.mp.br:4200/athenas/api/v2/ged/download/?file_id=28021'
    //     );
    //     // const url = window.URL.createObjectURL(new Blob([response.data]));
    //     const link = document.createElement('a');
    //     link.href = url;
    //     // link.setAttribute('download', title);
    //     document.body.appendChild(link);
    //     link.click();
    // }

    async download(file_id) {
        // const response = await apiGedDownload({
        //     file_id,
        // });

        useGedDownload(file_id);

        //local.mpmt.mp.br:4200/athenas/api/v2/ged/download/?file_id=28021&crowd.token_key=1zSgPUljMR6Zps0iTqAPNg00

        // this.forceFileDownload(response, 'arquivo');

        // let blob = new Blob([response], { type: 'application/pdf' });
        // const url = window.URL.createObjectURL(blob);
        // window.open(url);
        // console.log(response);

        // useDownload(uuid);
    }

    printCapacidade(classificacaoNumber: number) {
        return this.classificacoes.filter(classificacao => classificacao.value === classificacaoNumber)?.shift()?.label
    }

    exibirCapacidade(data) {
        return (data.capacity_label != undefined && (data.classificacao == undefined || data.classificacao === 1))
    }
}
