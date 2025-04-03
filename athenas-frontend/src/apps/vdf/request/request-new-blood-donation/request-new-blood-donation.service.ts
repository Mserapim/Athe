import { Injectable } from '@angular/core';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewElectoralSlackService } from '../request-new-electoral-slack/request-new-electoral-slack.service';
import { apiRhPvfRequestsUsufructsBloodDonationService } from 'api/rh/api-rh-pvf-requests-usufructs-blood-donation.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewBloodDonationService extends RequestNewElectoralSlackService {
    title;
    path;
    type_usufruct;
    apiService: any = apiRhPvfRequestsUsufructsBloodDonationService;

    constructor(protected currentUserService: CurrentUserService) {
        super(currentUserService);
    }
}
