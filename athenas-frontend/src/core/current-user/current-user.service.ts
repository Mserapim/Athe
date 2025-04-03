import { Injectable } from '@angular/core';
import {
    apiAuthCurrentUserService,
    AuthCurrentUserResponse,
} from 'api/auth/api-auth-current-user.service';
import { environment } from 'environments/environment';

@Injectable({
    providedIn: 'root',
})
export class CurrentUserService {
    private _currentUser: AuthCurrentUserResponse;

    constructor() {
        this.load();
    }

    get currentUser() {
        return this._currentUser;
    }

    get isSubstitutable(): boolean {
        return (
            this._currentUser.is_substitutable == 'OPTIONAL' ||
            this._currentUser.is_substitutable == 'REQUIRED'
        );
    }

    get isMember(): boolean {
        const type_by_possession =
            this._currentUser?.type_by_possession ||
            this._currentUser?.type_by_possesion; //FIX PARA TRASIÇÃO DE AMBIENTE
        return ['MBR', 'MEL'].includes(type_by_possession);
    }

    get isTrainne(): boolean {
        //Estagiário
        return this._currentUser?.type_by_possession == 'EST';
    }

    get isResidente(): boolean {
        //Estagiário
        return this._currentUser?.type_by_possession == 'RES';
    }

    async load() {
        if (this._currentUser) return this._currentUser;
        await this.reload();
        return this._currentUser;
    }

    async reload() {
        try {
            this._currentUser = await apiAuthCurrentUserService({});
            return this._currentUser;
        } catch (e) {
            console.log(e);
            debugger;
            window.location.href = environment.url_base;
        }
    }
}
