import {
    Component,
    EventEmitter,
    Input,
    OnDestroy,
    OnInit,
    Output,
    ViewEncapsulation,
} from '@angular/core';
import { environment } from 'environments/environment';
import { BaseComponent } from 'shared/base-component/base-component';
import { AuthCurrentUserResponse } from 'api/auth/api-auth-current-user.service';
import { Router } from '@angular/router';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { AtualizacaoCadastralEmailComponent } from 'apps/vdf/atualizacao-cadastral/atualizacao-cadastral-email/atualizacao-cadastral-email.component';
import { SessaoModuloService } from 'core/sessao/sessao-modulo.service';
import { map } from 'rxjs/operators';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { pvfAjudaService } from 'services/pvf-layout-ajuda.service';

@Component({
    selector: 'layout-padrao-cabecalho',
    templateUrl: './layout-padrao-cabecalho.component.html',
    encapsulation: ViewEncapsulation.None,
    exportAs: 'layout-padrao-cabecalho',
    standalone: false
})
export class LayoutPadraoCabecalhoComponent
    extends BaseComponent
    implements OnInit, OnDestroy
{
    @Input() isScreenSmall: boolean;
    @Output() toggleNavigationAppearance: EventEmitter<boolean> =
        new EventEmitter<boolean>();
    @Output() toggleNavigation: EventEmitter<boolean> =
        new EventEmitter<boolean>();

    usuario: AuthCurrentUserResponse;

    urlPortal: string = environment.url_base;

    constructor(
        private router: Router,
        public currentUserService: CurrentUserService,
        private atualizacaoCadastralEmailComponent: AtualizacaoCadastralEmailComponent,
        private sessaoModuloService: SessaoModuloService,
        private navegacaoAtualService: NavegacaoAtualService
    ) {
        super();
    }

    ngOnInit(): void {
        this.currentUserService.load().then(() => {
            this.usuario = this.currentUserService.currentUser;
        });
    }

    get title() {
        return this.navegacaoAtualService.moduloAtual$.pipe(
            map((x) => x?.nome)
        );
    }

    async goPortal() {
        window.location.href = this.urlPortal;
    }

    goClocking() {
        this.router.navigate([`vdf/registro-de-ponto/`]);
    }

    irAlterarEmailPessoal() {
        this.atualizacaoCadastralEmailComponent.abrir(true);
    }

    async logout() {}

    async irAjuda() {
        let moduloAtual = this.router.url.slice(1)
        let { link_de_ajuda } = await pvfAjudaService({sigla: moduloAtual})
        window.open(
            link_de_ajuda,
            '_blank'
        );
    }
}
