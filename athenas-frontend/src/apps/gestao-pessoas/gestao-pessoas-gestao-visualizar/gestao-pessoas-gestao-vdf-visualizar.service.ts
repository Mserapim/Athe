import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MpmtFormAutocompleteComponentItem } from 'components/mpmt-form-autocomplete/mpmt-form-autocomplete.component';

@Injectable()
export class GestaoPessoasGestaoVdfVisualizarService{
 
    filtros = new FormGroup({
        usuarios: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        tipos_solicitacoes: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        categorias: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        tipos_acoes: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        situacoes: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        periodo_tipo: new FormControl<"DT_SOL"|"DT_ACAO">("DT_SOL", []),
        periodo_em: new FormControl<Date[]>([], []),
    });

    constructor() {
    }

    

}
