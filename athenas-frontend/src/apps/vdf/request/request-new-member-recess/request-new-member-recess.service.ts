import { Injectable } from '@angular/core';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewElectoralSlackService } from '../request-new-electoral-slack/request-new-electoral-slack.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewMemberRecessService extends RequestNewElectoralSlackService {
    constructor(protected currentUserService: CurrentUserService) {
        super(currentUserService);
    }
}
