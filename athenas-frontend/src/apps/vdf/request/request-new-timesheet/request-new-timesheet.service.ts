import { Injectable } from '@angular/core';
import { CurrentUserService } from 'core/current-user/current-user.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewTimesheetService {
    title = 'Folha ponto';
    path = 'folhaponto';
    public subtitle = '';
    requestId: number;

    constructor(protected currentUserService: CurrentUserService) {}
}
