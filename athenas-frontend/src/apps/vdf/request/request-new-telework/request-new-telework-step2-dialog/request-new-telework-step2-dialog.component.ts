import { Component, Inject } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewTeleworkService } from '../request-new-telework.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { ApiRhPvfRequestsIdTeleworksTargetsItem } from 'api/rh/api-rh-pvf-requests-id-teleworks-targets.service';

@Component({
    selector: 'request-new-telework-step2-dialog',
    templateUrl: './request-new-telework-step2-dialog.component.html',
    standalone: false
})
export class RequestNewTeleworkStep2DialogComponent {
    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewTeleworkService,
        private dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        public data: ApiRhPvfRequestsIdTeleworksTargetsItem
    ) {}

    async ngOnInit() {}

    fechar() {
        this.dialog.closeAll();
    }
}
