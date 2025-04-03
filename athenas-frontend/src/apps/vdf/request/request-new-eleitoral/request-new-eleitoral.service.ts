import { Injectable } from '@angular/core';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { apiRhPvfRequestsUsufructsElectoralSlackService } from 'api/rh/api-rh-pvf-requests-usufructs-electoral-slack.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { addDay } from 'utils/add-day';
import { CurrentUserService } from 'core/current-user/current-user.service';
import {
    ApiRhPvfConfigRequestsAcquisitionPeriodsItem,
    apiRhPvfConfigRequestsAcquisitionPeriods,
} from 'api/rh/api-rh-pvf-config-requests-acquisition-periods.service';
import {
    apiPvfRequestsAbsencesHealthLicensesService
} from "../../../../api/rh/api-rh-pvf-requests-absences-health-licenses.service";
import {
    pvfRequestsAbsencesHealthFamilyLicensesService
} from "../../../../services/pvf-requests-absences-health-family-licenses.service";
import {ConfigRequestsTiposEleitoralEnum} from "../../../../enums/config-requests-tipos-eleitoral.enum";
import {Router} from "@angular/router";
import {RequestStepperService} from "../components/request-stepper/request-stepper.service";

@Injectable({
    providedIn: 'root',
})
export class RequestNewEleitoralService {
    title = 'Dispensa Eleitoral - TRE';
    subtitle = '';
    path = 'dispensa-eleitoral';
    type_usufruct = TypeUsufructEnum.FOLGA_ELEITORAL;
    rights: ApiRhPvfConfigRequestsAcquisitionPeriodsItem[];
    apiRights = apiRhPvfConfigRequestsAcquisitionPeriods;
    apiService: any = apiRhPvfRequestsUsufructsElectoralSlackService;
    message: string = '';
    minDate = new Date();
    items: any = [];
    itemsUsufruto: any = [];
    public typeId: number = null;

    type = new FormControl<'USUFRUTO' | 'VENDA' | null>('USUFRUTO', [
        Validators.required,
    ]);
    formUsufruct = new FormGroup({
        type: new FormControl<'USUFRUTO'>('USUFRUTO', [Validators.required]),
        start: new FormControl<Date | null>(null, [Validators.required]),
        days: new FormControl<number>(1, [Validators.required]),
        end: new FormControl<Date | null>(null, [Validators.required]),
    });
    formSell = new FormGroup({
        type: new FormControl<'VENDA'>('VENDA', [Validators.required]),
        days: new FormControl<number>(1, [Validators.required]),
        parcel: new FormControl<number | null>(null, [Validators.required]),
    });
    observation: string = '';
    public substitutes: [] = [];
    usufructs: {
        start: Date;
        end: Date;
        days: number;
    }[] = [];

    constructor(protected currentUserService: CurrentUserService,
                protected router: Router,
                protected stepper: RequestStepperService) {

    }

    populateUsufructs() {
        const x = [];
        for (let item of this.items) {
            if (item.type != 'USUFRUTO') continue;
            x.push({
                start_date: item.start,
                end_date: item.end,
                days: item.days,
            });
        }
        this.usufructs = x;
    }

    updateEndDate($event) {
        if (
            !this.formUsufruct.value.start ||
            !this.formUsufruct.value.days ||
            this.formUsufruct.value.days <= 0
        ) {
            this.formUsufruct.patchValue({
                end: undefined,
            });
            return;
        }

        const start = this.formUsufruct.value.start;
        const end = addDay(start, +this.formUsufruct.value.days - 1);

        this.formUsufruct.patchValue({
            end,
            start,
        });
    }

    addUsufruct() {
        if (!this.formUsufruct.valid) return;
        this.message = '';
        this.items.push(this.formUsufruct.value);
        this.formUsufruct.reset();
        this.formUsufruct.patchValue({ type: 'USUFRUTO', days: 1 });
        this.populateUsufructs();
    }

    addSell() {
        if (!this.formSell.valid) return;
        this.message = '';
        this.items.push(this.formSell.value);
        this.formSell.reset();
        this.formSell.patchValue({ type: 'VENDA', days: 1 });
    }

    removeItem(index: number) {
        this.items.splice(index, 1);
        this.message = '';
    }

    async confirm() {
        if (!this.isValidStep2) return;
        if (this.hasStep3 && !this.isValidStep3) return;
        const hasItemSell = this.items.find((x) => x.type == 'VENDA');
        let parcel_number = undefined;
        if (hasItemSell) parcel_number = hasItemSell.parcel;
        const payload = {
            observation: this.observation,
            parcel_number,
            substitutes: this.substitutes,
            usufructs_in: this.items.map((x) => {
                if (x.type == 'USUFRUTO')
                    return {
                        start_date: x.start,
                        end_date: x.end,
                        days: x.days,
                        sale_usufruct: 0,
                    };
                else
                    return {
                        start_date: null,
                        end_date: null,
                        days: x.days,
                        parcel_number,
                        sale_usufruct: 1,
                    };
            }),
        };

        const response = await this.apiService(payload);

        this.substitutes = [];
        this.items = [];
        this.observation = '';

        return response;
    }

    public async loadRights() {
        this.message = null;
        console.log(this.type_usufruct);

        const response = await this.apiRights({
            page: 1,
            per_page: 10,
            type_usufruct: this.type_usufruct,
        });

        this.rights = response.results;
    }

    get hasBalance() {
        if (!this.rights) return false;
        if (this.rights.length <= 0) return false;
        if (this.rights.find((x) => x.balance_available! > 0)) return true;
    }

    get canSell() {
        if (!this.rights) return false;
        if (this.rights.length <= 0) return false;
        return this.rights[0].sale_usufruct;
    }

    get isValidStep2() {
        return this.items.length > 0;
    }

    isValidStep3: boolean = false;

    get hasStep3() {
        this.itemsUsufruto = this.items.filter(item => item.type != 'VENDA');

        //Verifica se é somente venda
        if (this.itemsUsufruto.length >= 1) {
            return this.currentUserService.isSubstitutable
        } else {
            return false;
        }
    }

    get service() {
        if (
            this.typeId ==
            ConfigRequestsTiposEleitoralEnum.INCLUSAO_DIREITO
        )
            return apiPvfRequestsAbsencesHealthLicensesService;
        if (
            this.typeId ==
            ConfigRequestsTiposEleitoralEnum.FOLGA_ELEITORAL
        )
            return pvfRequestsAbsencesHealthFamilyLicensesService;

        throw 'SERVICE NOT IMPLEMENTED';

        return;
    }

    public goStep2() {
        if (
            this.typeId ==
            ConfigRequestsTiposEleitoralEnum.INCLUSAO_DIREITO
        ) {
            this.stepper.steps = ['Tipo de solicitação', 'Dados do formulário'];
            this.router.navigate([
                'vdf/solicitacoes/novo/credito-eleitoral',
                'step2'
            ]);
        }

        if (
            this.typeId ==
            ConfigRequestsTiposEleitoralEnum.FOLGA_ELEITORAL
        ) {
            this.stepper.steps = ['Tipo de solicitação', 'Saldos', 'Usufrutos', 'Substitutos'];
            this.router.navigate([
                'vdf/solicitacoes/novo/dispensa-eleitoral',
                'step2'
            ]);
        }
    }
}
