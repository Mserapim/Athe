
import { Injectable } from '@angular/core';
import { MpmtPickListService } from 'components/mpmt-picklist/mpmt-picklist.service';

@Injectable({
  providedIn: 'root'
})
export class PainelControleGrupoAtualizarUsuariosService extends MpmtPickListService {

    constructor() { 
        super()
    }
}