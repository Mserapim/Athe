import { Injectable } from '@angular/core';
import { apiRhPvfRequestsSchedulesRetifications } from 'api/rh/api-rh-pvf-requests-schedules-retifications.service';
import { RequestNewVactionsService } from '../request-new-vacations/request-new-vacations.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewRetificationService extends RequestNewVactionsService {
    public usufructs_ids: number[] = [];
    public total_days_to_retification = 30;

    public async confirm() {
        const payload = {
            observation: this.observation,
            usufructs_in: this.usufructs_in,
            usufructs_ids: this.usufructs_ids,
            substitutes: this.substitutes,
        };

        return await apiRhPvfRequestsSchedulesRetifications(payload);
    }
}
