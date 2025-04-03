import { Component } from '@angular/core';
import { PvfEmployePendingsDataSource } from 'datasources/pvf-employe-pendings.datasource';
import {
    ApiRhPvfMypendeciesResponseItem,
    apiRhPvfMypendeciesService,
} from 'api/rh/api-rh-pvf-mypendecies.service';
import { Router } from '@angular/router';
import { PendingTypeEnum } from 'enums/pending-type.enum';
import { MatDialog } from '@angular/material/dialog';
import { PrestacaoContasComponent } from 'apps/diarias/gestao/prestacao-contas/modal-prestacao-contas/modal-prestacao-contas.component';

@Component({
    selector: 'app-home-pendings',
    templateUrl: './home-pendings.component.html',
    styleUrls: ['./home-pendings.component.scss'],
    standalone: false
})
export class HomePendingsComponent {
    pendings = <ApiRhPvfMypendeciesResponseItem[]>[];

    ngOnInit() {
        this.loadPendings();
    }

    constructor(private _router: Router, public dialog: MatDialog) {}

    async go(item: ApiRhPvfMypendeciesResponseItem) {
        if (item.type == PendingTypeEnum.DESBLOQUEIO_TELETRABALHO)
            this._router.navigate([
                'vdf/solicitacoes/novo/teletrabalho-desbloqueio/step1',
            ]);
        if (item.type == PendingTypeEnum.APROVACOES_PENDENTES)
            this._router.navigate(['vdf/aprovacoes/pendentes']);
        if (item.type == PendingTypeEnum.REGISTRO_PONTO_ENTRADA)
            this._router.navigate(['vdf/registro-de-ponto']);
        if (item.type == PendingTypeEnum.ENVIO_TELETRABALHO_PENDENTE)
            this._router.navigate(['vdf/solicitacoes/novo/teletrabalho/step1']);
        if (item.type == PendingTypeEnum.RELATORIO_SEMESTRAL_PENDENTE)
            this._router.navigate([
                'vdf/solicitacoes/novo/relatorio-teletrabalho-semestral/step1',
            ]);
        if (item.type == PendingTypeEnum.PRESTACAO_CONTAS_DIARIAS) {
            this.dialog.open(PrestacaoContasComponent, {
                data: {
                    width: '50%',
                    height: '80%',
                    prestacao_contas_id: item.value,
                    onClose: () => this.loadPendings(),
                },
            });
        }
        if (item.type == PendingTypeEnum.APROVACOES_DIARIAS_PENDENTES) {
            this._router.navigate(['vdf/minhas-diarias/'], {
                queryParams: { situacao: 'Aguardando ciência' },
            });
        }
        if (item.type === PendingTypeEnum.AVALIACOES_PENDENTES_DIARIAS){
            if(item.value === 'pagamento'){
                this._router.navigate(['diarias/gestao/pagamentos']);
            }else if (item.value == 'prestacao'){
                this._router.navigate(['diarias/gestao/prestacao-contas']);
            }
            else{
                this._router.navigate(['diarias/gestao/viagens']);
            }
        }
    }

    async loadPendings() {
        const { results: pendings } = await apiRhPvfMypendeciesService({});
        this.pendings = pendings;
    }
}
