import { Component, ContentChild, EventEmitter, forwardRef, Injector, Input, OnChanges, OnDestroy, OnInit, Optional, Output, Self, TemplateRef } from '@angular/core';
import { AbstractControl, ControlValueAccessor, FormControl, FormGroup, NG_VALIDATORS, NG_VALUE_ACCESSOR, NgControl, ValidationErrors, Validator } from '@angular/forms';
import { ListPaginated } from 'api/@base/list-paginated';
import { BehaviorSubject, debounceTime, Subject, takeUntil } from 'rxjs';


export type MpmtFormSelecaoComponentItem = Record<string, any>;
export type MpmtFormSelecaoComponentFonteApi = (payload: {palavra_chave: string, per_page: number}) => Promise<ListPaginated<any>|MpmtFormSelecaoComponentItem[]>;

interface MpmtFormSelecaoComponentFilterEvent {
    originalEvent?: Event;
    filter: string;
    [key:string]: any
}

@Component({
    selector: 'mpmt-form-multiselecao',
    templateUrl: './mpmt-form-multiselecao.component.html',
    standalone: false,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtFormMultiselecaoComponent),
            multi: true,
        },
    ],
})
export class MpmtFormMultiselecaoComponent implements OnInit, OnChanges, ControlValueAccessor {

    @ContentChild('conteudoItem', { static: false }) conteudoItem!: TemplateRef<any>;
    @ContentChild('conteudoRodape', { static: false }) conteudoRodape!: TemplateRef<any>;

    @Input() fonte?: any[] | MpmtFormSelecaoComponentFonteApi;
    @Input() desabilitado?: boolean = false;
    @Input() titulo?: string = '';
    @Input() placeholder?: string = 'Selecione';
    @Input() atributoDisplay?: string = 'display';
    @Input() atributoChave?: string = 'pk';

    protected carregando: boolean = false;
    protected items: any[] = [];
    protected onChange: any = () => {};
    protected onTouched: any = () => {};
    protected ngControl: NgControl | null = null;
    protected form = null
    protected palavra_chave = null

    private recarregarSubject = new BehaviorSubject<number>(0);
    public destroy$ = new Subject<number>();

    constructor(private injector: Injector) {
        this.form = new FormGroup({
            valor: new FormControl<MpmtFormSelecaoComponentItem[]>([]),
        });

        this.recarregarSubject                                       
        .pipe(
            takeUntil(this.destroy$),
            debounceTime(500)
        )
        .subscribe(() => this.filtrar());
    }

    /**Ciclo de vida */
    ngOnInit() {
        this.ngControl = this.injector.get(NgControl, null); 
        if (this.ngControl) this.ngControl.valueAccessor = this;
        this.filtrarUmaVez({filter: ''});
    }
    
    ngOnChanges(changes) { }

    ngOnDestroy() {
        this.destroy$.next(0);
        this.destroy$.complete();
    }

    async aoSelecionar(event:any){
        this.form.get('valor').setValue(event?.value||[])
        this.onChange(this.form.get('valor').value);
        this.onTouched();
    }

    async construirFiltros() {
        return {
            palavra_chave: this.palavra_chave,
            per_page: 10
        }
    }

    async filtrar() {
        if (typeof this.fonte === 'function') {
            this.carregando = true;
            try {
                this.carregando = true
                const filtros = await this.construirFiltros()

                const result = await this.fonte(filtros);
                let items =[]
                if (Array.isArray(result)) {
                    items = result as any;
                } else {
                    items = result.results || [];
                }
                // Combine new items with currently selected values
                const allItems = [...items, ...(this.form?.get('valor')?.value || [])];
                
                // Remove duplicates based on the key attribute
                this.items = allItems.filter((item, index, self) => 
                    index === self.findIndex(t => t[this.atributoChave] === item[this.atributoChave])
                )
                // Sort items by display attribute (as strings to handle text properly)
                .sort((a, b) => String(a[this.atributoDisplay]).localeCompare(String(b[this.atributoDisplay])))
            } catch (error) {
                console.error('Error fetching items:', error);
                this.items = [];
            } finally {
                this.carregando = false;
            }
        } else if (Array.isArray(this.fonte)) {
            this.items = this.fonte.filter(item => 
                item[this.atributoDisplay].toLowerCase().includes(this.palavra_chave.toLowerCase())
            );
        }
    }


    filtrarUmaVez(event: MpmtFormSelecaoComponentFilterEvent){
        this.palavra_chave = event.filter;
        this.recarregarSubject.next(0);
    }

    /**ControlValueAccessor*/
    writeValue(value: MpmtFormSelecaoComponentItem[] | null): void {
        this.form.get('valor').setValue(value || []);
    }

    registerOnChange(fn: any): void {
        this.onChange = fn;
    }

    registerOnTouched(fn: any): void {
        this.onTouched = fn;
    }

    setDisabledState(isDisabled: boolean): void {
        this.desabilitado = isDisabled;
        if (isDisabled) {
            this.form.get('selected')?.disable({ emitEvent: false });
        } else {
            this.form.get('selected')?.enable({ emitEvent: false });
        }
    }

    mensagemDeErro(): string | undefined {
        if (this.ngControl?.control?.errors?.required) {
            return 'Este campo é obrigatório.';
        }
        return undefined;
    }
      
}
