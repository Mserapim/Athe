import { Component, Input, OnInit } from '@angular/core';
import { useGedDownload } from 'api/@base/use-ged-download';
import { printDate } from 'utils/print-date'
import {ActivatedRoute, Router} from "@angular/router";
import {RequestTypeEnum} from "../../../../../../enums/request-type.enum";
import {
    apiRhPvfRequestsAbsencesHealthLicensesId
} from "../../../../../../api/rh/api-rh-pvf-requests-absences-health-licenses-id.service";
import {
    apiRhPvfRequestsAbsencesHealthFamilyLicensesId
} from "../../../../../../api/rh/api-rh-pvf-requests-absences-health-family-licenses-id.service";
import {
    apiRhPvfRequestsAbsencesMourningAbsencesId
} from "../../../../../../api/rh/api-rh-pvf-requests-absences-mourning-absences-id.service";
import {
    apiRhPvfRequestsAbsencesMarriageAbsencesId
} from "../../../../../../api/rh/api-rh-pvf-requests-absences-marriage-absences-id.service";
import {
    apiRhPvfRequestsAbsencesPaternityAbsencesId
} from "../../../../../../api/rh/api-rh-pvf-requests-absences-paternity-absences-id.service";
import {
    apiRhPvfRequestsAbsencesMaternityAbsencesId
} from "../../../../../../api/rh/api-rh-pvf-requests-absences-maternity-absences-id.service";
import {
    apiRhPvfRequestsAbsencesBloodDonationId
} from "../../../../../../api/rh/api-rh-pvf-requests-absences-blood-donation-id.service";
import {
    apiVdfDetalhesSolicitacaoAuxilioCrecheIr, ApiVdfSolicitacaoAuxilioCrecheIrResponse
} from "../../../../../../api/vdf/api-vdf-solicitacao-aux-creche-ir-detalhes.service";

@Component({
    selector: 'request-show-solicitacao-auxilio-creche-ir',
    templateUrl: './request-show-solicitacao-auxilio-creche-ir.component.html',
    standalone: false
})
export class RequestShowSolicitacaoAuxilioCrecheIrComponent implements OnInit {
    @Input() requestId!: number;

    public data: ApiVdfSolicitacaoAuxilioCrecheIrResponse = {} as ApiVdfSolicitacaoAuxilioCrecheIrResponse;

    constructor(private route: ActivatedRoute, protected router: Router) {}

    ngOnInit() {
    }

    printDate = printDate;

    async ngOnChanges() {
        try {
            const response = await apiVdfDetalhesSolicitacaoAuxilioCrecheIr({
                id: this.requestId,
            });
            this.data = response;
        } catch (e) {
            console.error(e);
        }
    }

    async download(file_id) {
        useGedDownload(file_id);
    }

    getCapacidade(capacidade: number) {
        return capacidade == 1 ? 'Válido' : 'Inválido'
    }

    getDependenteIr(dependenteIr: boolean) {
        return dependenteIr == true ? 'É dependente' : 'Não é dependente'
    }

    getDependenteAuxilioCreche(dependenteAuxilioCreche: boolean) {
        return dependenteAuxilioCreche == true ? 'Sim' : 'Não';
    }
}
