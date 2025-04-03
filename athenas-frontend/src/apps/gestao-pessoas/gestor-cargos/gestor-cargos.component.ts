import { Component, OnInit } from '@angular/core';
import { MpmtPaginaDialogoService } from 'components/mpmt-pagina-dialogo/mpmt-pagina-dialogo.service';
import { GestorCargosService } from './gestor-cargos.service';
import { apiGestorCargosTipoLeiCargos } from 'api/gestao/api-gestao-pessoas-gestor-cargos-tipo-lei-cargos.service';

@Component({
    selector: 'gestor-cargos',
    templateUrl: 'gestor-cargos.component.html',
    standalone: false
})
export class GestorCargosComponent implements OnInit {
    apiGestorCargosTipoLeiCargos = apiGestorCargosTipoLeiCargos;
    
    constructor(
        public service: GestorCargosService,
        public mpmtPaginaDialogoService: MpmtPaginaDialogoService,
    ) {}

    ngOnInit() {
    }

}