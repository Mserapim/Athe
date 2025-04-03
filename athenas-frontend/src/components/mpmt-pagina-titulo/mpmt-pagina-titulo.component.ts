import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { apiPainelControleControleAcessoUsuarioMenuAtualizarFavoritos } from 'api/painel-controle/api-painel-controle-controle-acesso-usuario-menu-atualizar-favoritos.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { Menu } from 'core/tipos/Menu';
import { Subscription } from 'rxjs';

@Component({
    selector: 'mpmt-pagina-titulo',
    templateUrl: './mpmt-pagina-titulo.component.html',
    standalone: false
})
export class MpmtPaginaTituloComponent implements OnInit, OnDestroy {
    @Input('habilitar-favorito') habilitarFavorito: boolean = true;
    @Input('titulo') _titulo?: string;
    @Input('classes') classes?: string;

    protected paginaAtual: Menu;
    private subscription: Subscription;

    constructor(
        public navegacaoAtualService: NavegacaoAtualService,
        private currentUserService: CurrentUserService
    ) {}

    public async favoritar() {
        try {
            await apiPainelControleControleAcessoUsuarioMenuAtualizarFavoritos({
                menu_id: this.paginaAtual?.pk,
                servidor_id: this.currentUserService.currentUser?.id,
            });
            this.navegacaoAtualService.recarregar();
        } catch (e) {
            alert('Não é possivel adicionar mais favoritos');
        }
    }

    ngOnInit() {
        this.subscription = this.navegacaoAtualService.paginaAtual$.subscribe(
            (x) => (this.paginaAtual = x)
        );
    }

    ngOnDestroy(): void {
        this.subscription.unsubscribe();
    }

    get titulo() {
        return this._titulo || this.paginaAtual?.nome;
    }

    get favorito() {
        return this.paginaAtual?.favorito;
    }
}
