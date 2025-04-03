import { Component, Inject, OnInit } from '@angular/core';
import { apiRhPvfApprovalsRequestsId } from 'api/rh/api-rh-pvf-approvals-requests-id.service';
import { RequestShowUsufructComponent } from '../../request/request-show-usufruct/request-show-usufruct.component';

export class ApprovalShowUsufructComponentData {
    requestId: number;
}
@Component({
    selector: 'approval-show-usufruct',
    templateUrl: '../../request/request-show-usufruct/request-show-usufruct.component.html',
    standalone: false
})
export class ApprovalShowUsufructComponent extends RequestShowUsufructComponent {
    protected showActions = true;
    protected dialogClass = ApprovalShowUsufructComponent;
    get serviceDetail() {
        return apiRhPvfApprovalsRequestsId;
    }
    get canCancel() {
        return false;
    }
}
