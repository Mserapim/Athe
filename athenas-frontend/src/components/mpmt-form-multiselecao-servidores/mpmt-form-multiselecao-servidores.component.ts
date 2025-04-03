import { Component,  forwardRef, Injector, Input } from '@angular/core';
import { FormControl, FormGroup, NG_VALUE_ACCESSOR } from '@angular/forms';
import { apiVdfConfigRequestsServidores } from 'api/vdf/api-vdf-config-requests-servidores.service';
import { MpmtFormMultiselecaoComponent, MpmtFormSelecaoComponentItem } from 'components/mpmt-form-multiselecao/mpmt-form-multiselecao.component';

@Component({
    selector: 'mpmt-form-multiselecao-servidores',
    templateUrl: './mpmt-form-multiselecao-servidores.component.html',
    standalone: false,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtFormMultiselecaoServidoresComponent),
            multi: true,
        },
    ],
})
export class MpmtFormMultiselecaoServidoresComponent extends MpmtFormMultiselecaoComponent {

    protected apiVdfConfigRequestsServidores = apiVdfConfigRequestsServidores;
    protected form: FormGroup;

    @Input() titulo?: string = 'Servidores';
    @Input() placeholder?: string = 'Pesquisar por nome ou matricula';
    @Input() atributoDisplay?: string = 'nome';
    @Input() atributoValor?: string = 'pk';

    constructor(injector: Injector) {
        super(injector);

        this.fonte = apiVdfConfigRequestsServidores;
        this.form = new FormGroup({
            valor: new FormControl<MpmtFormSelecaoComponentItem[]>([]),
            somenteAtivo: new FormControl<boolean>(true)
        });
    }

    aoAlterarSomenteAtivo(event: any) {
        this.form.get('somenteAtivo')?.setValue(event.checked);
        this.filtrar();
    }

    override writeValue(value: any): void {
        if (value !== undefined && value !== null) {
            this.form.get('valor')?.setValue(value);
        }
    }

    override registerOnChange(fn: any): void {
        this.form.get('valor')?.valueChanges.subscribe(fn);
    }

    async construirFiltros() {
        return {
            palavra_chave: this.palavra_chave,
            per_page: 50,
            situacao: this.form.get('somenteAtivo')?.value?true:undefined
        }
    }

      
}
