import { Injectable } from '@angular/core';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewElectoralSlackService } from '../request-new-electoral-slack/request-new-electoral-slack.service';
import { apiRhPvfRequestsUsufructsServerShiftsService } from 'api/rh/api-rh-pvf-requests-usufructs-server-shifts.service';
import { apiRhPvfRequestsUsufructsForensicRecessService } from 'api/rh/api-rh-pvf-requests-usufructs-forensic-recess.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewForensicRecessService extends RequestNewElectoralSlackService {
    title;
    path;
    type_usufruct;
    apiService: any = apiRhPvfRequestsUsufructsForensicRecessService;

    constructor(protected currentUserService: CurrentUserService) {
        super(currentUserService);
    }
}
