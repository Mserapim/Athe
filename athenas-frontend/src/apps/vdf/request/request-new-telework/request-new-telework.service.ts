import { Injectable } from '@angular/core';
import { CurrentUserService } from 'core/current-user/current-user.service';
import {
    ApiRhPvfRequestsIdTeleworksTargetsItem,
    apiRhPvfRequestsIdTeleworksTargets,
} from 'api/rh/api-rh-pvf-requests-id-teleworks-targets.service';
import {
    ApiRhPvfRequestsIdResponse,
    apiRhPvfRequestsId,
} from 'api/rh/api-rh-pvf-requests-id.service';
import {
    ApiRhPvfConfigEmployeesTeleworksStatusResponseItem,
    apiRhPvfConfigEmployeesTeleworksStatus,
} from 'api/rh/api-rh-pvf-config-employees-teleworks-status.service';
import { apiRhPvfRequestsSendingTeleworksService } from 'api/rh/api-rh-pvf-requests-sending-teleworks.service';
import {
    ApiVdfRequestsSendingTeleworksAfastamentosItem,
    apiVdfRequestsSendingTeleworksAfastamentos,
} from 'api/vdf/api-vdf-requests-sending-teleworks-afastamentos.service';
import { apiVdfSolicitacaoFolhaPontoAfastamento } from 'api/vdf/api-vdf-solicitacao-folhaponto-afastamentos.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewTeleworkService {
    title = 'Teletrabalho';
    path = 'teletrabalho';
    public subtitle = '';
    public message = '';
    public messageSuccess = '';
    public messageError = '';

    public teleworkStatus: ApiRhPvfConfigEmployeesTeleworksStatusResponseItem;
    public request: ApiRhPvfRequestsIdResponse = {};
    public targets: ApiRhPvfRequestsIdTeleworksTargetsItem[];

    public observation = '';

    constructor(protected currentUserService: CurrentUserService) {}

    public aoInformarMetaAlcancada(
        target: ApiRhPvfRequestsIdTeleworksTargetsItem & {
            observation_required: boolean;
        }
    ) {
        if (target.total_completed >= target.meta_mes) {
            target.mark_situation = 1;
        }

        if (target.total_completed < target.meta_mes) {
            target.mark_situation = 2;
        }

        if (target.total_completed == 0) {
            target.mark_situation = 3;
        }

        if (target.mark_situation != 1) {
            target.observation_required = true;
        } else {
            target.observation_required = false;
        }
    }
    public async loadTargets() {
        const { results } = await apiRhPvfRequestsIdTeleworksTargets({
            requestId: this.request?.pk,
        });
        this.targets = results;
    }

    public async loadRequest({ requestId }: { requestId: number }) {
        const response = await apiRhPvfRequestsId({
            requestId,
        });
        this.request = response;

        return response;
    }

    async loadTeleworkStatus() {
        const response = await apiRhPvfConfigEmployeesTeleworksStatus({
            page: 1,
        });
        this.teleworkStatus = response;

        const { active_workplan, telework_id, telework_pending } = response;

        if (!active_workplan && !telework_pending) return;

        if (telework_id == 0) {
            await this.createRequest();
            return this.loadTeleworkStatus();
        }

        if (telework_id) {
            return await this.loadRequest({ requestId: telework_id });
        }
    }

    async loadTeleworkAfastamentos() {
        const response = await apiVdfSolicitacaoFolhaPontoAfastamento({
            page: 1,
        });
    }

    async createRequest() {
        const response = await apiRhPvfRequestsSendingTeleworksService({});
    }
}
