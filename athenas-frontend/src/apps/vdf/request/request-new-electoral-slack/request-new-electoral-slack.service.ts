import { Injectable } from '@angular/core';
import { apiRhPvfRequestsUsufructsIndividualVacationsService } from 'api/rh/api-rh-pvf-requests-usufructs-individual-vacations.service';
import { apiRhPvfRequestsUsufructsRegularVacations } from 'api/rh/api-rh-pvf-requests-usufructs-regular-vacations.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { apiRhPvfRequestsUsufructsElectoralSlackService } from 'api/rh/api-rh-pvf-requests-usufructs-electoral-slack.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { addDay } from 'utils/add-day';
import { CurrentUserService } from 'core/current-user/current-user.service';
import {
    ApiRhPvfConfigRequestsAcquisitionPeriodsItem,
    apiRhPvfConfigRequestsAcquisitionPeriods,
} from 'api/rh/api-rh-pvf-config-requests-acquisition-periods.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewElectoralSlackService {
    title = 'Dispensa Eleitoral';
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
        parcel: new FormControl<number | null>(1, [Validators.required]),
    });
    observation: string = '';
    public substitutes: [] = [];
    usufructs: {
        start: Date;
        end: Date;
        days: number;
    }[] = [];

    private _saldoVenda: number = 0;
    private _saldoUsufruto: number = 0;

    constructor(protected currentUserService: CurrentUserService) {}

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

        this._saldoVenda = this.rights.reduce((total, e) => total + (e.saldo_venda > 0 ? e.saldo_venda : 0), 0);
        this._saldoUsufruto = this.rights.reduce((total, e) => total + (e.balance_available || 0), 0);
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

    get saldoVenda(): number {
        return this._saldoVenda;
    }

    get saldoUsufruto(): number {
        return this._saldoUsufruto;
    }

    get temSaldoVenda(): boolean {
        return this.rights?.some(e => e.saldo_venda > 0) ?? false;
    }

    get totalDiasVenda(): number {
        return this.items
            .filter(i => i.type === 'VENDA')
            .reduce((sum, item) => sum + item.days, 0);
    }

    get totalDiasUsufruto(): number {
        return this.items
            .filter(i => i.type === 'USUFRUTO')
            .reduce((sum, item) => sum + item.days, 0);
    }
    
    get ultrapassaSaldoVenda(): boolean {
        return this.totalDiasVenda > this.saldoVenda;
    }

    get ultrapassaSaldoUsufruto(): boolean {
        return this.totalDiasUsufruto > this.saldoUsufruto;
    }
}
