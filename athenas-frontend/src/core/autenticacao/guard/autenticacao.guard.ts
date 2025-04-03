import { Injectable } from '@angular/core';
import {
    ActivatedRouteSnapshot,
    CanActivate,
    CanActivateChild,
    CanLoad,
    Route,
    Router,
    RouterStateSnapshot,
    UrlSegment,
    UrlTree,
} from '@angular/router';
import { Observable } from 'rxjs';
import { AutenticacaoService } from '../autenticacao.service';
import { environment } from 'environments/environment';
import { NgxPermissionsService } from 'ngx-permissions';
import { MensagemService } from 'core/mensagem/mensagem.service';

@Injectable({
    providedIn: 'root',
})
export class AutenticacaoGuard
    implements CanActivate, CanActivateChild, CanLoad
{
    /**
     * Constructor
     */
    constructor(
        private _autenticacaoService: AutenticacaoService,
        private _permissionsService: NgxPermissionsService,
        private _mensagem: MensagemService,
        private _router: Router
    ) {}

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Can activate
     *
     * @param route
     * @param state
     */
    canActivate(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ): Observable<boolean> | Promise<boolean> | boolean {
        return this.validarRota(route.data.permissoes);
    }

    /**
     * Can activate child
     *
     * @param childRoute
     * @param state
     */
    canActivateChild(
        childRoute: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ):
        | Observable<boolean | UrlTree>
        | Promise<boolean | UrlTree>
        | boolean
        | UrlTree {
        return this.validarRota(childRoute.data.permissoes);
    }

    /**
     * Can load
     *
     * @param route
     * @param segments
     */
    canLoad(
        route: Route,
        segments: UrlSegment[]
    ): Observable<boolean> | Promise<boolean> | boolean {
        return this.validarRota(route.data.permissoes);
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Private methods
    // -----------------------------------------------------------------------------------------------------

    private async validarRota(permissoes: string[]): Promise<boolean> {
        const logado = await this.validarUsuarioLogado();

        if (!logado) {
            window.location.href = environment.url_base;
            return false;
        } else {
            // logado.
            const autorizado: boolean = await this.validarPermissoes(
                permissoes
            );
            if (!autorizado) {
                return false;
            }
        }

        // Se as avaliações ocorreram com sucesso, return true.
        return true;
    }

    private async validarUsuarioLogado(): Promise<boolean> {
        return await this._autenticacaoService.validarUsuarioLogado();
    }

    private async validarPermissoes(permissoes: string[]): Promise<boolean> {
        if (!permissoes) {
            return true;
        }

        const autorizado = await this.validarAutorizacao(permissoes);

        if (!autorizado) {
            this._mensagem.erro(
                'Você não possui permissão para acessar este recurso!'
            );
            this._router.navigate(['404']);
            //window.location.href = environment.url_base;
            return false;
        }

        return true;
    }

    private async validarAutorizacao(permissoes: string[]): Promise<boolean> {
        return this._permissionsService
            .hasPermission(permissoes)
            .then((possuiPermissao: boolean) => {
                return possuiPermissao;
            });
    }
}
