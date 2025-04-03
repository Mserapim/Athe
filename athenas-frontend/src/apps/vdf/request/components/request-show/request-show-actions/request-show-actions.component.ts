import {
    Component,
    EventEmitter,
    Input,
    OnInit,
    Output,
    ViewChild,
} from '@angular/core';
import { FormControl, Validators } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MatTable } from '@angular/material/table';
import { ActivatedRoute, Router } from '@angular/router';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { apiRhPvfApprovalsRequestsIdActions } from 'api/rh/api-rh-pvf-approvals-requests-id-actions.service';
import { apiRhPvfApprovalsRequestsIdAuthorize } from 'api/rh/api-rh-pvf-approvals-requests-id-authorize.service';
import { apiRhPvfRequestsIdCancelService } from 'api/rh/api-rh-pvf-requests-id-cancel.service';
import { apiRhPvfRequestsIdExerciciosCumulativosSubstituicoes } from 'api/rh/api-rh-pvf-requests-id-exercicios-cumulativos-substituicoes.service';
import { ApiRhPvfRequestsIdResponse } from 'api/rh/api-rh-pvf-requests-id.service';
import { RequestStatusEnum, canRequestCancel } from 'enums/request-status.enum';
import { AtualizarExercicioCumulativoService } from '../request-show-exercicio-cumulativo/request-show-exercicio-cumulativo.service';
import { apiRhPublications } from 'api/publications/api-publications.service';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { RequestTypeEnum } from 'enums/request-type.enum';
import { RequestNewHorizontalProgressionsService } from '../../../request-new-horizontal-progressions/request-new-horizontal-progressions.service';
import { apiUpdateRhPvfRequestMovementsHorizontalProgression } from 'api/rh/api-rh-pvf-horizontal-progressions-current.service-put';
import { textoNormalMobile } from '../../../../../../utils/texto-normal-mobile';
import { VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirComponent } from 'apps/vdf/vdf-solicitacao-teletrabalho-desbloqueio-indeferir/vdf-solicitacao-teletrabalho-desbloqueio-indeferir.component';
import { FuseConfirmationService } from '@fuse/services/confirmation';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
    selector: 'request-show-actions',
    templateUrl: './request-show-actions.component.html',
    styleUrls: ['./request-show-actions.component.css'],
    standalone: false
})
export class RequestShowActionsComponent implements OnInit {
    @Input() request!: ApiRhPvfRequestsIdResponse;
    @Input() requestId!: number;
    @Input() showActions: boolean = true;
    @Output() changeRequest = new EventEmitter<ApiRhPvfRequestsIdResponse>();

    RequestType = RequestTypeEnum;

    public actions: any[] = [];
    public message: string = null;
    public observation = new FormControl('');

    searchKeyword: string = '';
    publications: any[] = [];
    selectedPublication: any = null;
    documents: any[] = [];
    file: any;
    isLoading: boolean = false;

    displayedColumns: string[] = ['description', 'originalName', 'id'];
    uploadedDocument: any;
    textoCancelar: string;

    searchPublications() {
        this.loadPublications(this.searchKeyword);
    }

    @ViewChild(MatTable) table: MatTable<any>;

    constructor(
        private route: ActivatedRoute,
        protected router: Router,
        private matDialog: MatDialog,
        private currentUserService: CurrentUserService,
        private eventExercicioCumulativo: AtualizarExercicioCumulativoService,
        protected service: RequestNewHorizontalProgressionsService,
        private _fuseConfirmationService: FuseConfirmationService,
        protected snackBar: MatSnackBar,
    ) {}

    ngOnInit() {
        this.loadActions({ requestId: this.requestId! });
        this.loadPublications();
        this.textoCancelar = textoNormalMobile(
            'Deseja cancelar essa solicitação?',
            'Cancelar'
        );

        const ehTeletrabalho = this.request.type_of_request == 'Teletrabalho';
        const temSaldoDevedor = this.request.metas_saldo_devedor?.length > 0;

        if (ehTeletrabalho && temSaldoDevedor) {
            this.observation.setValidators([Validators.required]);
        }

        this.observation.updateValueAndValidity();
    }

    get canCancel() {
        if (this.currentUserService.currentUser?.id != this.request.employee)
            return false;
        if (this.request.portal_request_type === 26)
            //Confirmação de realização do plantão
            return false;
        return canRequestCancel(this.request.status);
    }

    podeEnviar(): boolean {
        return (
            this.canCancel &&
            this.request.portal_request_type ===
                RequestTypeEnum.PROGRESSAO_HORIZONTAL &&
            this.request.status === RequestStatusEnum.AGUARDANDO_ENVIO
        );
    }

    protected async loadActions({ requestId }: { requestId: number }) {
        const { results: actions } = await apiRhPvfApprovalsRequestsIdActions({
            requestId,
        });

        this.actions = actions;
    }
    

    async reenviarRequest(documents) {
        try {
            this.isLoading = true;
            if (!this.documents.every((doc) => doc.description.trim() !== '')) {
                this.service.message =
                    'A descrição do arquivo deve ser preenchida.';
                return;
            }

            this.isLoading = true;
            const payload = {
                documents: documents,
            };

            const response =
                await apiUpdateRhPvfRequestMovementsHorizontalProgression(
                    this.requestId,
                    payload
                );
        } catch (e) {
            console.error(e);
        } finally {
            this.isLoading = false;
        }
        this.matDialog.closeAll();
    }

    public async selectAction(action: string, publicationId?: number){
        if (action === 'cancel'){
            return this.cancelApproveRequest(action)
        }
        if (action === 'deny'){
            return this.denyRequest(action)
        }
        return this.confirm(action, publicationId)
    }

    public async confirm(action: string, publicationId?: number) {
        this.isLoading = true;
        this.message = null;
        try {
            if (this.observation.invalid) {
                this.message = 'O campo de observação é obrigatório.';
                return;
            }
            if (
                action === 'deny' &&
                this.request.portal_request_type ===
                    RequestTypeEnum.DESBLOQUEIO_DO_TELETRABALHO
            ) {
                const solicitacao_id = this.request.pk;
                const dialogRef = this.matDialog.open(
                    VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirComponent,
                    {
                        width: '700px',
                        data: { solicitacao_id },
                    }
                );
                dialogRef.afterClosed().subscribe((result) => {
                    this.matDialog.closeAll();
                });

                return;
            }

            const payload = {
                action,
                requestId: this.requestId,
                observation: this.observation.value || '',
                publication: this.selectedPublication,
                documents: this.documents,
                anexos: [],
            };

            payload.anexos = this.documents.map((x) => {
                return x.attachment_id;
            });

            await apiRhPvfApprovalsRequestsIdAuthorize(payload);
            if (action === 'consolidated') {
                this.loadActions({ requestId: this.requestId! });
                this.dochangeExercicioCumulativo({
                    requestId: this.requestId!,
                });
            } else {
                this.matDialog.closeAll();
            }
        } catch (e) {
            console.log(e);
            this.message = e?.response?.data?.message;
        } finally {
            this.isLoading = false;
        }
    }

    public async denyRequest(action: string) {
        this.message = null;
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Tem certeza de que deseja indeferir esta solicitação? Essa ação não poderá ser desfeita.',
            icon: {
              show: true,
              name: 'heroicons_outline:exclamation',
              color: 'warn'
            },
            actions: {
                confirm: {
                  show: true,
                  label: 'Executar',
                  style: { 'background-color': '#dc2626' },                           
                },
                cancel: {
                  show: true,
                  label: 'Cancelar',
                  style: { 'background-color': '#cbd5e1' },
                }
            },
            dismissible: true
        });


        dialogRef.afterClosed().subscribe( async result => {
            if (result === 'confirmed') {
                if (
                    action === 'deny' &&
                    this.request.portal_request_type ===
                        RequestTypeEnum.DESBLOQUEIO_DO_TELETRABALHO
                ) {
                    const solicitacao_id = this.request.pk;
                    const dialogRef = this.matDialog.open(
                        VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirComponent,
                        {
                            width: '700px',
                            data: { solicitacao_id },
                        }
                    );
                    dialogRef.afterClosed().subscribe((result) => {
                        this.matDialog.closeAll();
                    });
    
                    return;
                }
                const payload = {
                    action,
                    requestId: this.requestId,
                    observation: this.observation.value || '',
                    publication: this.selectedPublication,
                    documents: [],
                    anexos: [],
                };
                if (
                    this.request.portal_request_type ===
                    RequestTypeEnum.PROGRESSAO_HORIZONTAL
                ) {
                    this.documents = this.documents.map((x) => {
                        return {
                            name: x.description,
                            attachment_id: x.fileId,
                        };
                    });
                }
    
                payload.anexos = this.documents.map((x) => {
                    return x.attachment_id;
                });
                try {
                    await apiRhPvfApprovalsRequestsIdAuthorize(payload);
                    this.matDialog.closeAll();
                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            }
        });
    }


    public async cancelApproveRequest(action: string) {
        this.message = null;
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Tem certeza de que deseja cancelar esta solicitação? Essa ação não poderá ser desfeita.',
            icon: {
              show: true,
              name: 'heroicons_outline:exclamation',
              color: 'warn'
            },
            actions: {
                confirm: {
                  show: true,
                  label: 'Executar',
                  style: { 'background-color': '#dc2626' },                           
                },
                cancel: {
                  show: true,
                  label: 'Cancelar',
                  style: { 'background-color': '#cbd5e1' },
                }
            },
            dismissible: true
        });


        dialogRef.afterClosed().subscribe( async result => {
            if (result === 'confirmed') {
                const payload = {
                    action,
                    requestId: this.requestId,
                    observation: this.observation.value || '',
                    publication: this.selectedPublication,
                    documents: [],
                    anexos: [],
                };
                if (
                    this.request.portal_request_type ===
                    RequestTypeEnum.PROGRESSAO_HORIZONTAL
                ) {
                    this.documents = this.documents.map((x) => {
                        return {
                            name: x.description,
                            attachment_id: x.fileId,
                        };
                    });
                }
    
                payload.anexos = this.documents.map((x) => {
                    return x.attachment_id;
                });
                try {
                    await apiRhPvfApprovalsRequestsIdAuthorize(payload);
                    this.matDialog.closeAll();
                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            }
        });
    }

    public async cancelRequest() {
        this.message = null;
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Tem certeza de que deseja cancelar esta solicitação? Essa ação não poderá ser desfeita.',
            icon: {
              show: true,
              name: 'heroicons_outline:exclamation',
              color: 'warn'
            },
            actions: {
                confirm: {
                  show: true,
                  label: 'Executar',
                  style: { 'background-color': '#dc2626' },                           
                },
                cancel: {
                  show: true,
                  label: 'Cancelar',
                  style: { 'background-color': '#cbd5e1' },
                }
            },
            dismissible: true
        });

        dialogRef.afterClosed().subscribe( async result => {
            if (result === 'confirmed') {
                try {
                    
                    await apiRhPvfRequestsIdCancelService({
                        requestId: this.requestId,
                    });
                    this.matDialog.closeAll();
                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            }
        });
    }

    protected exibirMensagem(
        titulo: string,
        texto: string,
        classe: string = 'custom-snackbar'
    ) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    async dochangeExercicioCumulativo({ requestId }: { requestId: number }) {
        const { results } =
            await apiRhPvfRequestsIdExerciciosCumulativosSubstituicoes({
                id: requestId,
            });
        this.eventExercicioCumulativo.emitEvent(
            'atualizarExercicioCumulativo',
            results
        );
    }

    // onSelectionChange, loadPublications e loadMore são referentes ao campo Publicação
    onSelectionChange(selected) {
        this.selectedPublication = selected ? selected.pk : null;
    }

    async loadPublications(keyword: string = '', page: number = 1) {
        try {
            const response = await apiRhPublications({
                keyword,
                page,
                per_page: 10,
            });
            if (page === 1) {
                this.publications = response.results;
            } else {
                this.publications = [...this.publications, ...response.results];
            }
        } catch (error) {
            console.error('Erro ao buscar publicações', error);
        }
    }

    displayFn(publication: any): string {
        return publication && publication.description
            ? publication.description
            : '';
    }

    loadMore() {
        const nextPage = this.publications.length / 10 + 1;
        this.loadPublications(this.searchKeyword, nextPage);
    }

    // removeItem e onFileInput são referentes ao campo Adicionar Arquivo
    removeItem(id: number) {
        this.documents = this.documents.filter((x) => x.id != id);
        this.table?.renderRows();
    }

    async onFileInput($file) {
        this.file = $file.target.files[0];
        const response = await gedUpload({
            file: this.file,
            fileName: this.file.name,
        });
        this.documents.push({
            id: new Date().getTime() + '',
            description: '',
            name: this.file.name,
            attachment_id: response.data.file_id,
            originalName: this.file.name,
        });
        this.table?.renderRows();
    }

    getStyle(actionLabel: string) {
        if (
            actionLabel.toLowerCase().includes('indeferir') ||
            actionLabel.toLowerCase().includes('cancelar')
        ) {
            return {
                'background-color': '#F87171',
            };
        } else if (
            actionLabel.toLowerCase().includes('deferir') ||
            actionLabel.toLowerCase().includes('confirmar') ||
            actionLabel.toLowerCase().includes('efetivar') ||
            actionLabel.toLowerCase().includes('aprovar')
        ) {
            return {
                'background-color': '#00AC81',
            };
        }

        return {
            'background-color': '#4F46E5',
        };
    }
}
