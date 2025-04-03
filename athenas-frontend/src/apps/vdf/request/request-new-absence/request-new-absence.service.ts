import { Injectable } from '@angular/core';
import { ConfigRequestsAbsencesTypesEnum } from 'enums/config-requests-absences-types.enum';
import { apiPvfRequestsAbsencesHealthLicensesService } from 'api/rh/api-rh-pvf-requests-absences-health-licenses.service';
import { Router } from '@angular/router';
import { pvfRequestsAbsencesHealthFamilyLicensesService } from 'services/pvf-requests-absences-health-family-licenses.service';
import { pvfRequestsAbsencesPaternityAbsencesService } from 'services/pvf-requests-absences-health-paternity-absences.service';
import { apiRhPvfRequestsAbsencesPaternityAbsencesService } from 'api/rh/api-rh-pvf-requests-absences-paternity-absences.service';
import { apiPvfRequestsAbsencesMourningAbsencesService } from 'api/rh/api-rh-pvf-requests-absences-mouning-absences.service';
import { apiPvfRequestsAbsencesMarriageAbsencesService } from 'api/rh/api-rh-pvf-requests-absences-marriage-absences.service';
import { apiPvfRequestsAbsencesBloodDonationService } from 'api/rh/api-rh-pvf-requests-absences-blood-donation.service';
import { apiRhPvfRequestsAbsencesMaternityAbsencesService } from 'api/rh/api-rh-pvf-requests-absences-maternity-absences.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewAbsenceService {
    public typeId: number = null;
    public message: string = '';
    public payload: any = {};

    public substitutes: {
        start_date: Date;
        end_date: Date;
        days?: number;
        substitute?: number;
        exercise?: number;
    }[] = [];

    constructor(private router: Router) {}

    public async confirm() {
        this.message = '';
        try {
            const payload = {
                ...this.payload,
                substitutes: this.substitutes,
            };
            const response = await this.service(payload);
            return response;
        } catch (e) {
            this.message = e.response?.data?.message;
            throw e;
        }
        return false;
    }

    get service() {
        if (
            this.typeId ==
            ConfigRequestsAbsencesTypesEnum.LICENCA_TRATAMENTO_SAUDE
        )
            return apiPvfRequestsAbsencesHealthLicensesService;
        if (
            this.typeId ==
            ConfigRequestsAbsencesTypesEnum.LICENCA_TRATAMENTO_SAUDE_PESSOA_FAMILIA
        )
            return pvfRequestsAbsencesHealthFamilyLicensesService;

        if (this.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_PATERNIDADE)
            return apiRhPvfRequestsAbsencesPaternityAbsencesService;

        if (this.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_MATERNIDADE)
            return apiRhPvfRequestsAbsencesMaternityAbsencesService;

        if (this.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_LUTO)
            return apiPvfRequestsAbsencesMourningAbsencesService;

        if (this.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_GALA)
            return apiPvfRequestsAbsencesMarriageAbsencesService;

        if (
            this.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_DOACAO_SANGUE
        )
            return apiPvfRequestsAbsencesBloodDonationService;

        throw 'SERVICE NOT IMPLEMENTED';
        // if (this.typeId == ConfigRequestsAbsencesTypes.LICENCA_DOACAO_SANGUE)
        //     return;

        return;
    }

    public goStep2() {
        if (
            this.typeId ==
            ConfigRequestsAbsencesTypesEnum.LICENCA_TRATAMENTO_SAUDE
        )
            this.router.navigate([
                'vdf/solicitacoes/novo/afastamentos',
                'step2',
                'health-license',
            ]);

        if (
            this.typeId ==
            ConfigRequestsAbsencesTypesEnum.LICENCA_TRATAMENTO_SAUDE_PESSOA_FAMILIA
        )
            this.router.navigate([
                'vdf/solicitacoes/novo/afastamentos',
                'step2',
                'health-license-family',
            ]);

        if (this.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_PATERNIDADE)
            return this.router.navigate([
                'vdf/solicitacoes/novo/afastamentos',
                'step2',
                'paternidade',
            ]);

        if (this.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_MATERNIDADE)
            return this.router.navigate([
                'vdf/solicitacoes/novo/afastamentos',
                'step2',
                'maternidade',
            ]);

        if (this.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_LUTO)
            this.router.navigate([
                'vdf/solicitacoes/novo/afastamentos',
                'step2',
                'mourning',
            ]);

        if (this.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_GALA)
            this.router.navigate([
                'vdf/solicitacoes/novo/afastamentos',
                'step2',
                'marriage',
            ]);

        if (
            this.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_DOACAO_SANGUE
        )
            this.router.navigate([
                'vdf/solicitacoes/novo/afastamentos',
                'step2',
                'blood-donation',
            ]);
    }
}
// public dates: {
//     start_date: Date;
//     end_date: Date;
//     days: number;
// }[] = [];
