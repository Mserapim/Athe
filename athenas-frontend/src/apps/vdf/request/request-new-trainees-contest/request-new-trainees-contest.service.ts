import { Injectable } from '@angular/core';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewElectoralSlackService } from '../request-new-electoral-slack/request-new-electoral-slack.service';
import { apiRhPvfRequestsUsufructsTraineesContestService } from 'api/rh/api-rh-pvf-requests-usufructs-trainees-contest.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewTraineesContextService extends RequestNewElectoralSlackService {
    title = 'Concurso de Estagiários';
    path = 'concurso-estagiario';
    type_usufruct = TypeUsufructEnum.CONCURSO_ESTAGIARIO;
    apiService: any = apiRhPvfRequestsUsufructsTraineesContestService;

    constructor(protected currentUserService: CurrentUserService) {
        super(currentUserService);
    }
}
