import { Component } from '@angular/core';
import { apiRhPvfApprovalsRequestsId } from 'api/rh/api-rh-pvf-approvals-requests-id.service';
import { RequestShowUsufructComponent } from '../../request/request-show-usufruct/request-show-usufruct.component';
import {textoNormalMobile} from "../../../../utils/texto-normal-mobile";

export class ApprovalShowTeleworkComponentData {
    requestId: number;
}
@Component({
    selector: 'approval-show-telework',
    templateUrl: '../../request/request-show-telework/request-show-telework.component.html',
    standalone: false
})
export class ApprovalShowTeleworkComponent extends RequestShowUsufructComponent {
    protected showActions = true;
    protected dialogClass = ApprovalShowTeleworkComponent;
    textoCancelar: string;

    get serviceDetail() {
        return apiRhPvfApprovalsRequestsId;
    }
    get canCancel() {
        return false;
    }

    ngOnInit() {
        super.ngOnInit();
        this.textoCancelar = textoNormalMobile("Deseja cancelar essa solicitação?", "Cancelar");
    }
}
