import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewTeleworkService } from '../request-new-telework.service';
import { apiRhPvfRequestsIdSendingTeleworksService } from 'api/rh/api-rh-pvf-requests-id-sending-teleworks.service';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { RequestNewTeleworkStep2DialogComponent } from '../request-new-telework-step2-dialog/request-new-telework-step2-dialog.component';
import { MatDialog } from '@angular/material/dialog';

@Component({
    selector: 'request-new-telework-step2',
    templateUrl: './request-new-telework-step2.component.html',
    styles: [
        `
            :host ::ng-deep .ck-editor__editable_inline {
                min-height: 180px;
            }
        `,
    ],
    standalone: false
})
export class RequestNewTeleworkStep2Component {
    file_id = null;
    file = null;
    filename = null;

    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected service: RequestNewTeleworkService,
        private _snackBar: MatSnackBar,
        private dialog: MatDialog
    ) {
        stepper.currentStep = 1;
    }

    async ngOnInit() {
        this.service.loadTargets();
        this.file_id = this.service.request.anexo_id;
        this.filename = this.service.request.anexo_name;
    }

    explicarDialog(data: any) {
        let dialogRef = this.dialog.open(
            RequestNewTeleworkStep2DialogComponent,
            {
                data,
            }
        );
    }

    get isValid() {
        if (!this.service.targets) return false;
        return !this.service.targets.some((x) => {
            if (!x.mark_situation) return true;
            if (
                x.total_completed == null ||
                x.total_completed == undefined ||
                x.total_completed < 0
            )
                return true;
            if (
                x.observation_required &&
                (!x.observation || x.observation.trim().length <= 0)
            ) {
                return true;
            }
            return false;
        });
    }

    options = [
        {
            value: 1,
            label: 'Alcançada',
        },
        {
            value: 2,
            label: 'Parcialmente Alcançada',
        },
        {
            value: 3,
            label: 'Não Alcançada',
        },
    ];

    goBack() {
        this.router.navigate([`vdf/solicitacoes/novo/teletrabalho`, 'step1']);
    }

    async onFileInput($file) {
        try {
            this.file = $file.target.files[0];
            const response = await gedUpload({
                file: this.file,
                fileName: this.file.name,
                format_valid: 'PDF',
            });
            this.file_id = response.data.file_id;
        } catch (e) {
            this.file = null;
            this.showMessage(e?.response?.data?.message);
        }
    }

    showMessage(mensagem: string) {
        this._snackBar.open(mensagem, '', {
            duration: 4000,
            panelClass: ['custom-snackbar'],
            verticalPosition: 'top',
        });
    }

    async goConfirm() {
        try {
            const response = await apiRhPvfRequestsIdSendingTeleworksService({
                id: this.service.request.pk,
                targets: this.service.targets.map((x) => {
                    return {
                        id: x.id,
                        total_completed: x.total_completed,
                        mark_situation: x.mark_situation,
                        observation: x.observation,
                        anexo_id: x.anexo_id,
                    };
                }),
                observation: this.service.observation,
                anexo_id: this.file_id,
            });
            await this.goRequests();
            this.service.observation = '';
        } catch (e) {}
    }

    goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }
}
