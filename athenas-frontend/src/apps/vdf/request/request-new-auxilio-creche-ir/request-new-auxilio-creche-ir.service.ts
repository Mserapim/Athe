import { Injectable } from '@angular/core';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

@Injectable({
    providedIn: 'root',
})
export class RequestNewAuxilioCrecheIrService {
    title = 'Auxílio creche e/ou dependente de IRRF';
    path = 'auxilio-creche-ir';
}
