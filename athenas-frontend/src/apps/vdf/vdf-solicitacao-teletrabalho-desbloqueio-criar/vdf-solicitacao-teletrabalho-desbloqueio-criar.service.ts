import { Injectable } from '@angular/core';
import { CurrentUserService } from 'core/current-user/current-user.service';

@Injectable({
    providedIn: 'root',
})
export class VdfSolicitacaoTeletrabalhoDesbloqueioService {
    title = 'Solicitação de Desbloqueio';
    path = 'vdf-solicitacao-teletrabalho-desbloqueio';
    public subtitle = '';
    requestId: number;

    constructor(protected currentUserService: CurrentUserService) {}
}
