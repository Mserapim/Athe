import { Component, OnDestroy, OnInit, ViewEncapsulation } from '@angular/core';
import { BaseComponent } from 'shared/base-component/base-component';
import { Router } from '@angular/router';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { Modulo } from 'core/tipos/modulo';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'layout-modulos',
    templateUrl: './layout-modulos.component.html',
    encapsulation: ViewEncapsulation.None,
    exportAs: 'layout-modulos',
    standalone: false
})
export class LayoutModulosComponent
    extends BaseComponent
    implements OnInit, OnDestroy
{
    modulos: Modulo[] = [];
    modulo: Modulo;
    aberto: boolean = false;

    constructor(
        private router: Router,
        public currentUserService: CurrentUserService,
        public navegacaoAtualService: NavegacaoAtualService
    ) {
        super();
    }

    subscriptions = new Subscription();
    ngOnInit() {
        const subscription1 = this.navegacaoAtualService.modulos$.subscribe(
            (x) => (this.modulos = x)
        );

        const subscription2 = this.navegacaoAtualService.moduloAtual$.subscribe(
            (x) => (this.modulo = x)
        );

        this.subscriptions.add(subscription1);
        this.subscriptions.add(subscription2);
    }

    ngOnDestroy(): void {
        this.subscriptions.unsubscribe();
    }

    exibir() {
        this.aberto = true;
    }

    fechar() {
        this.aberto = false;
    }

    irAthenas() {
        window.open('https://athenas.mpmt.mp.br/', '_blank');
    }

    irModulo(modulo: Modulo) {
        this.navegacaoAtualService.trocarModulo(modulo);
        this.aberto = false;
    }
}
