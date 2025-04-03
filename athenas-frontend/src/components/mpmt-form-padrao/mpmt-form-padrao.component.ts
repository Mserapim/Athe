import { Component,  forwardRef, Injector, Input, OnChanges,  OnInit } from '@angular/core';
import { ControlValueAccessor,  NG_VALUE_ACCESSOR, NgControl } from '@angular/forms';


@Component({
    template: '',
})
export abstract class MpmtFormPadraoComponent<T>
implements OnInit, OnChanges, ControlValueAccessor{

    @Input() desabilitado?: boolean = false;
    @Input() titulo?: string = '';
    @Input() placeholder?: string = 'Selecione';

    protected onChange: any = () => {};
    protected onTouched: any = () => {};
    protected ngControl: NgControl | null = null;

    protected abstract valor: T | null

    constructor(private injector: Injector) {
    }

    /** ciclo de vida */
    ngOnInit() {
        this.ngControl = this.injector.get(NgControl, null); 
        if (this.ngControl) this.ngControl.valueAccessor = this;
    }

    ngOnChanges(changes) { }

    /**ControlValueAccessor*/
    writeValue(value: T | null): void {
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
