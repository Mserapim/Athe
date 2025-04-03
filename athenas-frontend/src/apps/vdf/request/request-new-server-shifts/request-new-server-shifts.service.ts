import { Injectable } from '@angular/core';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewElectoralSlackService } from '../request-new-electoral-slack/request-new-electoral-slack.service';
import { apiRhPvfRequestsUsufructsServerShiftsService } from 'api/rh/api-rh-pvf-requests-usufructs-server-shifts.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewServerShiftsService extends RequestNewElectoralSlackService {
    type_usufruct = TypeUsufructEnum.PLANTAO_SERVIDORES;
    apiService: any = apiRhPvfRequestsUsufructsServerShiftsService;

    constructor(protected currentUserService: CurrentUserService) {
        super(currentUserService);
    }
}
