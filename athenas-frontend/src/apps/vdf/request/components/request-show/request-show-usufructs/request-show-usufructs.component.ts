import { Component, Inject, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import {
    AuthCurrentUserResponse,
    apiAuthCurrentUserService,
} from 'api/auth/api-auth-current-user.service';
import {
    ApiRhPvfApprovalsRequestsIdResponse,
    apiRhPvfApprovalsRequestsId,
} from 'api/rh/api-rh-pvf-approvals-requests-id.service';
import {
    ApiRhPvfRequestsIdUsufructsResponseItem,
    apiPOSTRhPvfRequestsIdUsufructs,
    apiRhPvfRequestsIdUsufructs,
} from 'api/rh/api-rh-pvf-requests-id-usufructs.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Component({
    selector: 'request-show-usufructs',
    templateUrl: './request-show-usufructs.component.html',
    standalone: false
})
export class RequestShowUsufructsComponent implements OnInit {
    @Input() requestId!: number;

    displayedColumns = ['start_date', 'end_date', 'days'];

    message = '';
    payment_competence_bkp: string;
    payment_installments_bkp: number;
    status: string = '';
    groupIds: number[] = [];
    canEdit: boolean = false;

    public results: ApiRhPvfRequestsIdUsufructsResponseItem[] = [];

    constructor(private route: ActivatedRoute, protected router: Router) {}

    ngOnInit() {
        this.initializeComponent();
    }

    private async initializeComponent() {
        await this.load({ requestId: this.requestId! });
        await this.determineEditingPermission();
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } = await apiRhPvfRequestsIdUsufructs({
            requestId,
            per_page: 100,
        });
        this.results = results;

        const typesUsufruct = [
            TypeUsufructEnum.FERIAS_REGULAMENTARES,
            TypeUsufructEnum.FERIAS_INDIVIDUAIS,
        ];

        if (results.some(item => typesUsufruct.includes(item.type_usufruct))) {
            this.displayedColumns = [
                ...this.displayedColumns,
                'payment_competence',
                results.some(item => item.type_usufruct === TypeUsufructEnum.FERIAS_INDIVIDUAIS) 
                    ? 'numero_parcela' 
                    : 'payment_installments',
                'editar',
            ];
        }
    }

    async determineEditingPermission() {
        try {
            const requestStatus = await this.getRequestStatus(this.requestId);
            const currentUser = await this.getCurrentUser();

            this.groupIds = currentUser.group_ids;

            const isAprovServidores = this.groupIds.includes(159); //mpmt-perfil-vdf-aprovador-servidores
            const isAprovMembros = this.groupIds.includes(160); //mpmt-perfil-vdf-aprovador-membros

            const isStatusValid =
                requestStatus.status_name === 'Aguardando Efetivação' ||
                requestStatus.status_name === 'Aguardando Aprovador' ||
                requestStatus.status_name ===
                    'Aguardando Assessoria da Corregedoria';

            this.canEdit =
                isStatusValid &&
                ((isAprovServidores &&
                    this.results.some(
                        (item) =>
                            item.type_usufruct ===
                            TypeUsufructEnum.FERIAS_REGULAMENTARES
                    )) ||
                    (isAprovMembros &&
                        this.results.some(
                            (item) =>
                                item.type_usufruct ===
                                TypeUsufructEnum.FERIAS_INDIVIDUAIS
                        )));
        } catch (error) {
            console.error('Erro ao determinar a permissão de edição:', error);
            this.canEdit = false;
        }
    }

    async getRequestStatus(
        requestId: number
    ): Promise<ApiRhPvfApprovalsRequestsIdResponse> {
        try {
            const response = await apiRhPvfApprovalsRequestsId({ requestId });
            return response;
        } catch (error) {
            console.error('Erro ao obter o status do request:', error);
            throw error;
        }
    }

    async getCurrentUser(): Promise<AuthCurrentUserResponse> {
        try {
            const response = await apiAuthCurrentUserService({});
            this.groupIds = response.group_ids;
            return response;
        } catch (error) {
            console.error('Erro ao obter informações do usuário atual:', error);
            throw error;
        }
    }

    enableEditing(element: any) {
        this.payment_competence_bkp = element.payment_competence;
        this.payment_installments_bkp = element.payment_installments;
        element.isEditing = true;
    }

    cancelEditing(element: any) {
        element.payment_competence = this.payment_competence_bkp;
        element.payment_installments = this.payment_installments_bkp;
        element.isEditing = false;
    }

    async save(element: any) {
        this.message = '';
        if (
            !this.isValid(
                element.payment_competence,
                element.payment_installments
            )
        ) {
            this.cancelEditing(element);
            return;
        }
        element.isEditing = false;

        const response = await apiPOSTRhPvfRequestsIdUsufructs({
            requestId: this.requestId,
            pk: element.pk,
            start_date: element.start_date,
            end_date: element.end_date,
            days: element.days,
            type_usufruct: element.type_usufruct,
            payment_competence: element.payment_competence,
            payment_installments: element.payment_installments,
            numero_parcela: element.numero_parcela,
        });
    }

    isValid(competencia: string, parcela: number): boolean {
        if (parcela <= 0 || !parcela || parcela >= 99) {
            this.message = 'O valor da parcela deve estar em 1 e 99';
        }

        if (competencia) {
            const competenceList = competencia.split('/', 2);

            const month = Number(competenceList[0]);
            if (isNaN(month) || month < 1 || month > 12) {
                this.message = 'O mês da competência deve estar entre 01 e 12';
                return false;
            }

            const year = Number(competenceList[1]);
            if (
                isNaN(year) ||
                year < 1970 ||
                year > new Date().getFullYear() + 10
            ) {
                this.message = 'O ano da competência deve ser um ano válido';
                return false;
            }
        }
        return true;
    }
}
