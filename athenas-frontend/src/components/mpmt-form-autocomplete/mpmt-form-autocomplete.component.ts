import { Component, EventEmitter, forwardRef, Injector, Input, OnChanges, OnDestroy, OnInit, Optional, Output, Self } from '@angular/core';
import { AbstractControl, ControlValueAccessor, NG_VALIDATORS, NG_VALUE_ACCESSOR, NgControl, ValidationErrors, Validator } from '@angular/forms';
import { ListPaginated } from 'api/@base/list-paginated';
import { AutoCompleteSelectEvent } from 'primeng/autocomplete';

export type MpmtFormAutocompleteComponentItem = Record<string, any>;
export type MpmtFormAutocompleteComponentFonteApi = (payload: {palavra_chave: string, per_page: number}) => Promise<ListPaginated<any>|MpmtFormAutocompleteComponentItem[]>;

interface MpmtFormAutocompleteComponentAutoCompleteCompleteEvent {
    originalEvent: Event;
    query: string;
}

@Component({
    selector: 'mpmt-form-autocomplete',
    templateUrl: './mpmt-form-autocomplete.component.html',
    standalone: false,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtFormAutocompleteComponent),
            multi: true,
        },
    ],
})
export class MpmtFormAutocompleteComponent 
implements OnInit, OnChanges, ControlValueAccessor{

    @Input() fonte?: any[] | MpmtFormAutocompleteComponentFonteApi;
    @Input() desabilitado?: boolean = false;
    @Input() titulo?: string = '';
    @Input() multiplos?: boolean = false;
    @Input() placeholder?: string = 'Selecione';
    @Input() atributoDisplay?: string = 'display';

    protected items: any[] = [];
    protected valor: MpmtFormAutocompleteComponentItem |  MpmtFormAutocompleteComponentItem[] | undefined;
    protected onChange: any = () => {};
    protected onTouched: any = () => {};
    protected ngControl: NgControl | null = null;

    /**Ciclo de vida */
    constructor(private injector: Injector) {}

    ngOnInit() {
        this.ngControl = this.injector.get(NgControl, null); 
        if (this.ngControl) this.ngControl.valueAccessor = this;
    }

    ngOnChanges(changes) {
        if(!this.valor) if(this.multiplos) this.valor = []
    }
    /** */
    async  pesquisar(event: MpmtFormAutocompleteComponentAutoCompleteCompleteEvent) {
        if(!this.fonte) return this.items = []

        if(this.fonte instanceof Function){
            const response = await this.fonte({palavra_chave: event.query, per_page: 10})

            if(response instanceof Array) this.items = response
            else this.items = response.results.map(item => ({
                    ...item, 
                    id: item.value, 
                    value: undefined /** fix Se passar value não funciona */
                }))
        }else{
            this.items = this.fonte 
        }
    }

    selecionarValor(event:AutoCompleteSelectEvent){
        this.onChange(this.valor)
    }

    /**ControlValueAccessor*/
    writeValue(value: MpmtFormAutocompleteComponentItem| null): void {
        this.valor = value;
    }

    registerOnChange(fn: any): void {
        this.onChange = fn;
    }
    registerOnTouched(fn: any): void {
        this.onTouched = fn;
    }

    setDisabledState?(isDisabled: boolean): void {
        setTimeout(() => {
            this.desabilitado = isDisabled;
        }, 10);
    }

    mensagemDeErro(): string {
        if (this.ngControl?.control?.errors?.required) {
          return 'Este campo é obrigatório.';
        }
    }
      
}
