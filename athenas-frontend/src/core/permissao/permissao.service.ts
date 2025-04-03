import { Injectable } from '@angular/core';
// import { Apollo, gql } from "apollo-angular";
import { first, firstValueFrom, map, Observable, of } from 'rxjs';
import { NgxPermissionsService } from 'ngx-permissions';
import { QueryConsultarPermissoes } from './permissao.types';
import { environment } from 'environments/environment';

// const QUERY_CONSULTAR_PERMISSOES = gql`
//   query {
//     consultarPermissoes
//   }
// `;

@Injectable({
    providedIn: 'root',
})
export class PermissaoService {
    constructor(
        // private _apollo: Apollo,
        private _permissionsService: NgxPermissionsService
    ) {}

    private consultarPermissoes(): Observable<void> {
        const perm = ['ADMIN', 'EDITOR'];

        this._permissionsService.loadPermissions(perm);

        return new Observable();

        // return this._apollo.watchQuery<QueryConsultarPermissoes>({
        //     query: QUERY_CONSULTAR_PERMISSOES
        // }).valueChanges.pipe(map(({ data }) => {
        //     if (!data || !data.consultarPermissoes || data.consultarPermissoes.length === 0)
        //         window.location.href = environment.url_base;

        //     this._permissionsService.loadPermissions(data.consultarPermissoes);
        // }));
    }

    async obterTodasPermissoesUsuario() {
        const permissoes$ = this.consultarPermissoes().pipe(first());
        return await firstValueFrom(permissoes$);
    }
}
