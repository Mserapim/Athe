import { Injectable } from '@angular/core';
import { CurrentUserService } from 'core/current-user/current-user.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewRelatorioTeletrabalhoSemestralService {
    title = 'Relatório Semestral de Teletrabalho';
    path = 'relatorio-teletrabalho-semestral';
    public subtitle = '';
    requestId: number;

    constructor(protected currentUserService: CurrentUserService) {}
}
