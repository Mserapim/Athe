import {
    Component,
    Input,
    OnDestroy,
    OnInit,
    ViewEncapsulation,
} from '@angular/core';
import { environment } from 'environments/environment';
import { BaseComponent } from 'shared/base-component/base-component';
import { AuthCurrentUserResponse } from 'api/auth/api-auth-current-user.service';
import { Router } from '@angular/router';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { AtualizacaoCadastralEmailComponent } from 'apps/vdf/atualizacao-cadastral/atualizacao-cadastral-email/atualizacao-cadastral-email.component';

@Component({
    selector: 'layout-padrao-usuario',
    templateUrl: './layout-padrao-usuario.component.html',
    encapsulation: ViewEncapsulation.None,
    exportAs: 'layout-padrao-usuario',
    standalone: false
})
export class LayoutPadraoUsuarioComponent
    extends BaseComponent
    implements OnInit, OnDestroy
{
    @Input() showName: boolean = false;
    usuario: AuthCurrentUserResponse;

    urlPortal: string = environment.url_base;

    constructor(
        private router: Router,
        public currentUserService: CurrentUserService,
        private atualizacaoCadastralEmailComponent: AtualizacaoCadastralEmailComponent
    ) {
        super();
    }

    ngOnInit(): void {
        this.currentUserService.load().then(() => {
            this.usuario = this.currentUserService.currentUser;
        });
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
}
