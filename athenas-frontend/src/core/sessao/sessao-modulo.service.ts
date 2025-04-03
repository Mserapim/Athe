import { Injectable } from '@angular/core';
import { Modulo } from 'core/tipos/modulo';

@Injectable({
    providedIn: 'root',
})
export class SessaoModuloService {
    public modulo: Modulo;

    constructor() {}
}
