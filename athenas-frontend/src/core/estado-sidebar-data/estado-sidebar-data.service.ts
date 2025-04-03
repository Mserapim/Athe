import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class EstadoSidebarDataService {
    constructor() {}

    public atualizarEstadoSidebar$: BehaviorSubject<boolean> =
        new BehaviorSubject(false);
    public atualizarVisibilidadeSidebar$: BehaviorSubject<boolean> =
        new BehaviorSubject(true);

    public atualizarEstadoSidebar(fechado: boolean): void {
        this.atualizarEstadoSidebar$.next(fechado);
    }

    public atualizarVisibilidadeSidebar(visivel: boolean): void {
        this.atualizarVisibilidadeSidebar$.next(visivel);
    }
}
