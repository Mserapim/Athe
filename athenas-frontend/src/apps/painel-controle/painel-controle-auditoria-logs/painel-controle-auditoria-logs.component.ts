import { Component, OnInit } from '@angular/core';
import { AuditoriaLogsService } from './painel-controle-auditoria-logs.service';
import { MpmtPaginaDialogoService } from 'components/mpmt-pagina-dialogo/mpmt-pagina-dialogo.service';
import { apiAuditoriaModelosLogs } from 'api/painel-controle/api-painel-controle-modelos-logs.service';

@Component({
    selector: 'auditoria-logs',
    templateUrl: 'painel-controle-auditoria-logs.component.html',
    standalone: false
})
export class AuditoriaLogsComponent implements OnInit {
    apiAuditoriaModelosLogs = apiAuditoriaModelosLogs;
    
    acoes_logs = [
        { label: "create", value: 0 },
        { label: "update", value: 1 },
        { label: "delete", value: 2 },
    ];
    
    
    constructor(
        public service: AuditoriaLogsService,
        public mpmtPaginaDialogoService: MpmtPaginaDialogoService,
    ) {}

    ngOnInit() {
    }

}