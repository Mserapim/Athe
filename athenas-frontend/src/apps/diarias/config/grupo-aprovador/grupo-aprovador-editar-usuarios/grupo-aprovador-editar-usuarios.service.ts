import { Injectable } from '@angular/core';
import { MpmtPickListService } from 'components/mpmt-picklist/mpmt-picklist.service';

@Injectable({
  providedIn: 'root'
})
export class DiariasGrupoAprovadorEditarUsuariosService extends MpmtPickListService {

    constructor() { 
        super()
    }
}