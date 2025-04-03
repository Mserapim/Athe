import { Injectable } from '@angular/core';
import { apiVdfSolicitacaoFolgaService } from 'api/vdf/api-vdf-solicitacao-folga-criar.service';
import { CurrentUserService } from 'core/current-user/current-user.service';


@Injectable({
    providedIn: 'root',
})
export class RequestNewSolicitacaoFolgaService {
    title = 'Solicitação Folga';
    path = 'Solicitação Folga';

    public message: string = '';
    public payload: any = {};

    constructor(protected currentUserService: CurrentUserService) {}

    public async confirm() {
        this.message = '';
        try {
            const payload = {
                ...this.payload
            };
            const response = await apiVdfSolicitacaoFolgaService(payload);
            return response;
        } catch (e) {
            this.message = e.response?.data?.message;
            throw e;
        }
        return false;
    }


}
