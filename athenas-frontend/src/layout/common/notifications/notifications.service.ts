import { Injectable } from '@angular/core';
import {
    BehaviorSubject,
    firstValueFrom,
    from,
    observable,
    Observable,
    of,
    ReplaySubject,
} from 'rxjs';
import { Notification, ToastAction } from './notifications.types';
import { map, switchMap, take, tap } from 'rxjs/operators';
import { apiAdmNotificacoesHermes } from 'api/adm/api-adm-notificacoes-hermes.service';

@Injectable({
    providedIn: 'root',
})
export class NotificationsService {
    private _notifications: ReplaySubject<Notification[]> = new ReplaySubject<
        Notification[]
    >(1);

    private toastId: BehaviorSubject<ToastAction> =
        new BehaviorSubject<ToastAction>(new ToastAction(0, false));
    toastId$: Observable<ToastAction> = this.toastId.asObservable();

    /**
     * Constructor
     */
    constructor() {}

    // -----------------------------------------------------------------------------------------------------
    // @ Accessors
    // -----------------------------------------------------------------------------------------------------

    /**
     * Getter for notifications
     */
    get notifications$(): Observable<Notification[]> {
        return this._notifications.asObservable();
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Get all notifications
     */
    listarNotificacoes(
        pagina = 1,
        notificacoesPorPagina = 10
    ): Observable<(Notification | any)[]> | any {
        return apiAdmNotificacoesHermes({
            page: pagina,
            per_page: notificacoesPorPagina,
        });
    }

    getToastId(): ToastAction {
        return this.toastId.value;
    }

    setToastId(id: number, touched: boolean): void {
        this.toastId.next(new ToastAction(id, touched));
    }
}
