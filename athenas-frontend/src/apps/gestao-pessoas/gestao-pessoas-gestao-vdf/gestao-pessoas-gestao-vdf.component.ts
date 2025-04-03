import { Component, ViewChild, OnInit } from '@angular/core';
import { GestaoPessoasGestaoVdfService } from './gestao-pessoas-gestao-vdf.service';
import { apiRhPvfConfigRequestsTypes } from 'api/rh/api-rh-pvf-config-requests-types.service';
import { apiRhPvfConfigRequestsStatus } from 'api/rh/api-rh-pvf-config-requests-status.service';
import { apiRhPvfConfigRequestsEmployeeTypes } from 'api/rh/api-rh-pvf-config-requests-employee-types.service';
import { apiVdfConfigRequestsAcoesService } from 'api/vdf/api-vdf-config-requests-acoes.service';
import { apiRhSevidoresService } from 'api/rh/api-rh-servidores.service';
import { GestaoPessoasGestaoVdfVisualizarComponent } from '../gestao-pessoas-gestao-visualizar/gestao-pessoas-gestao-vdf-visualizar.component';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { MpmtPaginaDialogoService } from 'components/mpmt-pagina-dialogo/mpmt-pagina-dialogo.service';
import { apiReportRhGestaoVdfService } from 'api/report/api-report-rh-gestao-vdf';
import { apiVdfConfigRequestsServidores } from 'api/vdf/api-vdf-config-requests-servidores.service';

@Component({
    selector: 'gestao-pessoas-gestao-vdf',
    templateUrl: 'gestao-pessoas-gestao-vdf.component.html',
    standalone: false,
})
export class GestaoPessoasGestaoVdfComponent implements OnInit {

    apiRhSevidoresService = apiRhSevidoresService
    apiRhPvfConfigRequestsTypes = apiRhPvfConfigRequestsTypes
    apiRhPvfConfigRequestsStatus = apiRhPvfConfigRequestsStatus
    apiRhPvfConfigRequestsEmployeeTypes = apiRhPvfConfigRequestsEmployeeTypes
    apiVdfConfigRequestsAcoesService = apiVdfConfigRequestsAcoesService
    apiVdfConfigRequestsServidores = apiVdfConfigRequestsServidores

    constructor(
        public service: GestaoPessoasGestaoVdfService,
        public mpmtPaginaDialogoService: MpmtPaginaDialogoService,
        private  gestaoPessoasGestaoVdfVisualizarComponent: GestaoPessoasGestaoVdfVisualizarComponent
    ) {}

    ngOnInit() {
        // this.gestaoPessoasGestaoVdfVisualizarComponent.abrir({solicitacaoId: '1'});
    }

   

}