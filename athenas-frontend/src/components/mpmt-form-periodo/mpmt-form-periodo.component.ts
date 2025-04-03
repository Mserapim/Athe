import { Component, EventEmitter, forwardRef, Injector, Input, OnChanges, OnDestroy, OnInit, Optional, Output, Self } from '@angular/core';
import { ControlValueAccessor, NG_VALIDATORS, NG_VALUE_ACCESSOR, NgControl, ValidationErrors, Validator } from '@angular/forms';
import { MpmtFormPadraoComponent } from 'components/mpmt-form-padrao/mpmt-form-padrao.component';


@Component({
    selector: 'mpmt-form-periodo',
    templateUrl: './mpmt-form-periodo.component.html',
    standalone: false,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtFormPeriodoComponent),
            multi: true,
        },
    ],
})
export class MpmtFormPeriodoComponent  extends MpmtFormPadraoComponent<Date[]> 
implements OnInit, OnChanges, ControlValueAccessor{
 
    protected valor: Date[] =[] 

    constructor(injector: Injector) {
        super(injector)
    }

    selecionar(event: Date){
        if (Array.isArray(this.valor) && this.valor.length === 2) {
            this.onChange(this.valor);
            this.onTouched();
        }
    }
      
}
