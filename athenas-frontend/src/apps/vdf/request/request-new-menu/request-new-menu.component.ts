import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute, Router } from '@angular/router';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { apiRhPvfConfigUserTypesRequestService } from 'api/rh/api-rh-pvf-config-user-types-request.service';
import { apiRhPvfConfigEmployeesTimesheetStatus } from '../../../../api/rh/api-rh-pvf-config-employees-timesheet-status.service';

export class RequestNewMenuComponentData {
    close: () => void;
}
@Component({
    selector: 'request-new-menu',
    templateUrl: './request-new-menu.component.html',
    standalone: false
})
export class RequestNewMenuComponent implements OnInit {
    query: string = '';
    menu: any[];
    filtered = [];

    warningMessage: string = '';
    hasPendingTeleworkRequest: boolean = false;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private currentUserService: CurrentUserService,
        private snackBar: MatSnackBar,
        @Inject(MAT_DIALOG_DATA) public payload: any
    ) {}

    async loadMenuByUser() {
        const { results } = await apiRhPvfConfigUserTypesRequestService({});

        const codes = results.map((x) => x.value);
        this.menu = this.MENU.filter((x) => {
            return codes.includes(x.code) || x.code == 'AFASTAMENTOS';
        });

        this.filter();
    }

    async ngOnInit() {
        this.hasPendingTeleworkRequest = this.payload.hasPendingTeleworkRequest;
        this.loadMenuByUser();
    }

    filter() {
        if (this.query == '') this.filtered = this.menu;
        this.filtered = this.menu.filter(
            (x) =>
                x.label.toLowerCase().includes(this.query.toLowerCase()) ||
                x.description.toLowerCase().includes(this.query.toLowerCase())
        );
    }

    async goLink(menuItem) {
        if (
            menuItem.code === 'TELETRABALHO' &&
            this.hasPendingTeleworkRequest
        ) {
            this.snackBar.open(
                'Já existe uma solicitação de Teletrabalho/Cancelamento aguardando aprovação no momento.',
                '',
                {
                    duration: 4000,
                    panelClass: ['custom-snackbar'],
                    verticalPosition: 'top',
                }
            );
        } else if (menuItem.code === 'FOLHA_PONTO') {
            await this.createRequestAndValidTimesheet(menuItem);
        } else {
            this.router.navigate([menuItem.routerLink]);
        }
        this.payload.close();
    }

    async createRequestAndValidTimesheet(menuItem) {
        try {
            const { timesheet_id, active_workplan, timesheet_pending } =
                await apiRhPvfConfigEmployeesTimesheetStatus({
                    page: 1,
                });

            if (timesheet_pending === true) {
                this.snackBar.open(
                    'Já existe uma solicitação de folha ponto em andamento.',
                    '',
                    {
                        duration: 4000,
                        panelClass: ['custom-snackbar'],
                        verticalPosition: 'top',
                    }
                );
            } else {
                this.router.navigate([menuItem.routerLink]);
            }
        } catch (e) {
            this.snackBar.open(
                e?.response?.data?.message ||
                    'Erro inesperado ao criar solicitação',
                '',
                {
                    duration: 4000,
                    panelClass: ['custom-snackbar'],
                    verticalPosition: 'top',
                }
            );
            throw e;
        }
    }

    MENU: {
        code: string;
        routerLink: string;
        label: string;
        icon: string;
        description: string;
    }[] = [
        {
            code: 'FERIAS_REGULAMENTARES',
            routerLink: '/vdf/solicitacoes/novo/ferias/step1',
            label: 'Férias',
            description: 'Servidores efetivos, comissionados e estagiários',
            icon: '',
        },
        {
            code: 'FERIAS_INDIVIDUAIS',
            routerLink: '/vdf/solicitacoes/novo/ferias/step1',
            label: 'Férias Individuais',
            description: 'Membros',
            icon: '',
        },
        {
            code: 'RECESSO_ESTAGIARIO',
            routerLink: '/vdf/solicitacoes/novo/ferias/step1',
            label: 'Recesso Estagiário',
            description: 'Estagiários',
            icon: '',
        },
        {
            code: 'RECESSO_RESIDENTE',
            routerLink: '/vdf/solicitacoes/novo/ferias/step1',
            label: 'Recesso Residente',
            description: 'Residentes',
            icon: '',
        },
        {
            code: 'RETIFICACAO',
            routerLink: '/vdf/solicitacoes/retificacoes/step1',
            label: 'Retificação de Férias e usufrutos',
            description: 'Retificação de férias, usufrutos',
            icon: 'heroicons_outline:face-frown',
        },
        {
            code: 'AFASTAMENTOS',
            routerLink: '/vdf/solicitacoes/novo/afastamentos/step1',
            label: 'Licenças e Afastamentos',
            description: 'Licença Saúde, pessoa na família, luto, gala, ...',
            icon: 'heroicons_outline:face-frown',
        },
        {
            code: 'CANCELAMENTO',
            routerLink: '/vdf/solicitacoes/cancelamento/step1',
            label: 'Cancelamentos',
            description: 'Cancelamento de uma solicitação já efetivada',
            icon: '',
        },
        {
            code: 'PROGRESSAO_HORIZONTAL',
            routerLink: '/vdf/solicitacoes/progressao-horizontal/step1',
            label: 'Progressão Horizontal',
            description: 'Progressão para classes B, C, D. ',
            icon: '',
        },

        {
            code: 'FOLGA_ELEITORAL',
            routerLink: '/vdf/solicitacoes/novo/dispensa-eleitoral/step1',
            label: 'Dispensa Eleitoral - TRE',
            description: 'Referente à convocação da justiça eleitoral ou referente a serviços prestados à justiça eleitoral',
            icon: '',
        },
        {
            code: 'RECESSO_FORENSE',
            routerLink: '/vdf/solicitacoes/novo/recesso-forense/step1',
            label: 'Recesso Forense',
            description:
                'Correspondente ao trabalho durante periodo de recesso',
            icon: '',
        },
        {
            code: 'CONCURSO_ESTAGIARIOS',
            routerLink: '/vdf/solicitacoes/novo/concurso-estagiario/step1',
            label: 'Concurso  de Estagiários',
            description:
                'Correspondente ao exercício em concurso de estagiários',
            icon: '',
        },
        {
            code: 'PLANTOES‌_SERVIDORES',
            routerLink: '/vdf/solicitacoes/novo/plantao-servidor/step1',
            label: 'Plantão',
            description: 'Compensação por relação de plantão',
            icon: '',
        },
        {
            code: 'DOACAO_SANGUE',
            routerLink: '/vdf/solicitacoes/novo/doacao-sangue/step1',
            label: 'Doação de Sangue',
            description: 'Usufruto compensatório referente a doação de sangue',
            icon: '',
        },
        {
            code: 'FOLGAS_COMPENSATORIAS_MEMBROS',
            routerLink: '/vdf/solicitacoes/novo/folga-compensatoria/step1',
            label: 'Folga compensatórias',
            description: 'Compensação por dia trabalhado em plantão',
            icon: '',
        },
        {
            code: 'PLANTAO_DE_RECESSO_FORENSE',
            routerLink:
                '/vdf/solicitacoes/novo/recesso-forense-de-membros/step1',
            label: 'Plantão  de Recesso Forense - Membros',
            description:
                'Compensação por plantão realizado durante o recesso - Membros',
            icon: '',
        },
        {
            code: 'CONCURSO_PROMOTOR_SUBSTITUTO',
            routerLink:
                '/vdf/solicitacoes/novo/concurso-promotor-substituto/step1',
            label: 'Concurso de Promotor Substituto',
            description: 'Concurso de Promotor Substituto',
            icon: '',
        },
        {
            code: 'TELETRABALHO',
            routerLink: '/vdf/solicitacoes/novo/teletrabalho/step1',
            label: 'Teletrabalho',
            description: 'Envio de relatório de teletrabalho mensal',
            icon: '',
        },
        {
            code: 'FOLHA_PONTO',
            routerLink: '/vdf/solicitacoes/novo/folhaponto/step1',
            label: 'Folha Ponto',
            description: 'Envio mensal da folha ponto',
            icon: '',
        },
        {
            code: 'EXERCICIO_CUMULATIVO',
            routerLink: '/vdf/solicitacoes/novo/exercicio-cumulativo/step1',
            label: 'Exercicio Cumulativo de Substituições',
            description: 'Venda de Substituições em Promotores/Procuradorias',
            icon: '',
        },
        {
            code: 'RELATORIO_SEMESTRAL_TELETRABALHO',
            routerLink:
                '/vdf/solicitacoes/novo/relatorio-teletrabalho-semestral/step1',
            label: 'Relatório Teletrabalho Semestral',
            description:
                'Solicitação de entrega Relatório Teletrabalho Semestral',
            icon: '',
        },
        {
            code: 'SOLICITACAO_FOLGA',
            routerLink: '/vdf/solicitacoes/novo/solicitacao-folga/step1',
            label: 'Solicitar Crédito de Folgas',
            description:
                'Auxílio Eleitoral, Concurso, Conselho tutelar, Juizado do Torcedor...',
            icon: '',
        },
        {
            code: 'SOLICITACAO_AUX_CRECHE_IR',
            routerLink: '/vdf/solicitacoes/novo/auxilio-creche-ir/step1',
            label: 'Auxilio creche e/ou Dependente de IRRF',
            description:
                'Solicitação para recebimento de auxílio creche e inclusão do dependente para IRRF',
            icon: '',
        },
        {
            code: 'DESBLOQUEIO_TELETRABALHO',
            routerLink: 'vdf/solicitacoes/novo/teletrabalho-desbloqueio/step1',
            label: 'Desbloqueio de teletrabalho',
            description: 'Sol. desbloqueio teletrabalho',
            icon: '',
        },
    ];
}
