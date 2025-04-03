import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';

@Component({
    selector: 'mpmt-pagina',
    templateUrl: './mpmt-pagina.component.html',
    standalone: false,
})
export class MpmtPaginaComponent {
    @Input('bloqueado') bloqueado?: boolean;

    constructor(public navegacaoAtualService: NavegacaoAtualService) {}
}
