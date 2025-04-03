import { Dialog } from '@angular/cdk/dialog';
import { Component, Inject, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import {
    ApiRhPvfRequestsIdHistoriesResponseItem,
    apiRhPvfRequestsIdHistories,
} from 'api/rh/api-rh-pvf-requests-id-histories.service';
import {
    RequestObservationComponent,
    RequestObservationComponentData,
} from '../../request-observation/request-observation.component';
import { MatDialog } from '@angular/material/dialog';
import { EditObservationModalComponent } from '../request-show-observation-retification/request-show-observation-retification.component';
import {
    apiAuthCurrentUserService,
    GroupDetail,
} from 'api/auth/api-auth-current-user.service';
import { useGedDownload } from 'api/@base/use-ged-download';
import { DateAdapter } from '@angular/material/core';

@Component({
    selector: 'request-show-historic',
    templateUrl: './request-show-historic.component.html',
    standalone: false
})
export class RequestShowHistoricComponent implements OnInit {
    @Input() requestId!: number;

    displayedColumns = [
        'group',
        'date',
        'employee',
        'action_label',
        'observation',
        'anexos',
    ];

    public results: ApiRhPvfRequestsIdHistoriesResponseItem[] = [];
    private userGroupDetails: GroupDetail[] = [];

    constructor(
        private route: ActivatedRoute,
        private dialog: MatDialog,
        protected router: Router,
        protected dateAdapter: DateAdapter<Date>
    ) {
        this.dateAdapter.setLocale('pt-BR');
    }

    async ngOnInit() {
        const currentUser = await apiAuthCurrentUserService({});
        this.userGroupDetails = currentUser.group_details;
        this.load({ requestId: this.requestId! });
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } = await apiRhPvfRequestsIdHistories({
            requestId,
        });
        this.results = results;
        const isUserInCogerGroup = this.userGroupDetails.some(
            (group) =>
                group.name === 'mpmt-perfil-vdf-aprovador-assessoria-coger'
        );
        const hasCogerObservation = results.some(
            (el) => el.group === 'COGER' && el.action_label === 'Anotação'
        );

        if (
            !this.displayedColumns.includes('action') &&
            isUserInCogerGroup &&
            hasCogerObservation
        ) {
            this.displayedColumns.push('action');
        }
    }

    async download(file_id) {
        useGedDownload(file_id);
    }

    goDetail(row?) {
        event?.stopPropagation();
        const dialogRef = this.dialog.open(RequestObservationComponent, {
            width: '90%',
            data: <RequestObservationComponentData>{
                observation: row?.observation || '',
                close: (response?) => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
                // this.applyFilter();
            }
        });
    }

    openEditModal(row: ApiRhPvfRequestsIdHistoriesResponseItem) {
        const dialogRef = this.dialog.open(EditObservationModalComponent, {
            width: '90%',
            data: {
                observation: row.observation,
                pk: row.pk,
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
                this.load({ requestId: this.requestId });
            }
        });
    }

    format30Chars(htmlContent: string): string {
        if (!htmlContent) return '';
        // Remove tags HTML
        const plainText = htmlContent.replace(/<\/?[^>]+(>|$)/g, '');
        // Retorna os primeiros 30 caracteres
        return (
            plainText.substring(0, 30) + (plainText.length > 30 ? '...' : '')
        );
    }
}
