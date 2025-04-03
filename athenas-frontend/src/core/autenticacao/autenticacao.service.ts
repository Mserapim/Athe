import { Injectable } from '@angular/core';
import { Apollo } from 'apollo-angular';
import { map } from 'rxjs/operators';
import { gql } from '@apollo/client/core';
import { Observable, first, firstValueFrom } from 'rxjs';

const QUERY_IS_LOGGED = gql`
    {
        isLogged
    }
`;
const QUERY_LOGOUT = gql`
    {
        logout
    }
`;

@Injectable({
    providedIn: 'root',
})
export class AutenticacaoService {
    constructor(private _apollo: Apollo) {}

    private isUsuarioLogado(): Observable<boolean> {
        return this._apollo
            .watchQuery({
                query: QUERY_IS_LOGGED,
            })
            .valueChanges.pipe(
                map((res) => {
                    return res.data['isLogged'];
                })
            );
    }

    async validarUsuarioLogado(): Promise<boolean> {
        const isUsuarioLogado$ = this.isUsuarioLogado().pipe(first());
        return await firstValueFrom(isUsuarioLogado$);
    }

    logout(): any {
        return this._apollo
            .watchQuery<any>({
                query: QUERY_LOGOUT,
            })
            .valueChanges.pipe(
                map(({ data }) => {
                    return data;
                })
            );
    }

    limparDadosPosLogout(): void {
        // Reset store on logout.
        // reset the store after that
        this._apollo.client.resetStore();
    }
}
