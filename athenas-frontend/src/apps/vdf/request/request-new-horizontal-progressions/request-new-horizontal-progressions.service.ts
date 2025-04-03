import { Injectable } from '@angular/core';
import { CurrentUserService } from 'core/current-user/current-user.service';
import {
    ApiRhPvfHorizontalProgressionsCurrentResponseItem,
    apiRhPvfHorizontalProgressionsCurrent,
} from 'api/rh/api-rh-pvf-horizontal-progressions-current.service';
import {
    ApiRhPvfHorizontalProgressionsNextResponseItem,
    apiRhPvfHorizontalProgressionsNext,
} from 'api/rh/api-rh-pvf-horizontal-progressions-next.service';
import { apiRhPvfRequestsMovementsHorizontalProgressions } from 'api/rh/api-rh-pvf-requests-movements-horizontal-progressions.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewHorizontalProgressionsService {
    title = 'Progressão Horizontal';
    path = 'progressao-horizontal';

    message: string = '';
    selectedCurrent: number = undefined;
    selectedNext: number = undefined;
    documents: {
        name: string;
        attachment_id: number;
    }[] = [];
    termo_aceite: boolean = false;

    currents: ApiRhPvfHorizontalProgressionsCurrentResponseItem[] = [];
    nexts: ApiRhPvfHorizontalProgressionsNextResponseItem[] = [];

    constructor(protected currentUserService: CurrentUserService) {}

    async loadCurrentes() {
        const { results } = await apiRhPvfHorizontalProgressionsCurrent({});
        this.currents = results;
    }

    async loadNexts() {
        const { results } = await apiRhPvfHorizontalProgressionsNext({});
        this.nexts = results;
    }

    async goConfirm() {
        this.message = '';
        const response = await apiRhPvfRequestsMovementsHorizontalProgressions({
            progression: this.selectedCurrent,
            config: this.selectedNext,
            documents: this.documents,
            termo_aceite: this.termo_aceite,
        });
        if (response.success === false) {
            this.message = response.message;
        }
    }
}
