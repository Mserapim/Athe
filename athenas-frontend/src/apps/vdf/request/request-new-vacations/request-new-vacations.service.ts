import { Injectable } from '@angular/core';
import { apiRhPvfRequestsUsufructsIndividualVacationsService } from 'api/rh/api-rh-pvf-requests-usufructs-individual-vacations.service';
import { apiRhPvfRequestsUsufructsRegularVacations } from 'api/rh/api-rh-pvf-requests-usufructs-regular-vacations.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { apiRhPvfRequestsUsufructsInternRecess } from 'api/rh/api-rh-pvf-requests-usufructs-intern-recess.service';
import {
    apiRhPvfRequestsUsufructsResidenteRecess
} from "../../../../api/rh/api-rh-pvf-requests-usufructs-residente-recess.service";

@Injectable({
    providedIn: 'root',
})
export class RequestNewVactionsService {
    public type: 'REGULAR' | 'INDIVIDUAL' | 'ESTAGIARIO' | 'RESIDENTE';
    public observation: string = '';
    public parcel_number: number = 0;
    public totalDays: number = 0;

    public usufructs_in: {
        start_date: Date;
        end_date: Date;
        days?: number;
        parcel_number?: number;
        sale_usufruct?: number;
    }[] = [];

    public substitutes: {
        start_date: Date;
        end_date: Date;
        substitute: number;
        exercise: number;
    }[] = [];

    public async confirm() {
        let service;
        let type_usufruct;
        if (this.type == 'INDIVIDUAL') {
            type_usufruct = TypeUsufructEnum.FERIAS_INDIVIDUAIS;
            service = apiRhPvfRequestsUsufructsIndividualVacationsService;
        }
        if (this.type == 'REGULAR') {
            type_usufruct = TypeUsufructEnum.FERIAS_REGULAMENTARES;
            service = apiRhPvfRequestsUsufructsRegularVacations;
        }
        if (this.type == 'ESTAGIARIO') {
            service = apiRhPvfRequestsUsufructsInternRecess;
            type_usufruct = TypeUsufructEnum.RECESSO_DE_ESTAGIARIOS;
        }
        if (this.type == 'RESIDENTE') {
            service = apiRhPvfRequestsUsufructsResidenteRecess;
            type_usufruct = TypeUsufructEnum.RECESSO_DE_ESTAGIARIOS;
        }

        const payload = {
            observation: this.observation,
            usufructs_in: this.usufructs_in,
            substitutes: this.substitutes,
            parcel_number: 0,
            type_usufruct,
        };

        return await service(payload);
    }
}
