import { Component,  forwardRef, inject, Injector, Input, OnChanges,  OnInit } from '@angular/core';
import { ControlValueAccessor,  NG_VALUE_ACCESSOR, NgControl } from '@angular/forms';
import { MpmtFormPadraoComponent } from 'components/mpmt-form-padrao/mpmt-form-padrao.component';


@Component({
    selector: 'mpmt-form-botao-selecao',
    templateUrl: './mpmt-form-botao-selecao.component.html',
    standalone: false,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtFormBotaoSelecaoComponent),
            multi: true,
        },
    ],
})
export class MpmtFormBotaoSelecaoComponent  extends MpmtFormPadraoComponent<string|number> 
implements OnInit, OnChanges, ControlValueAccessor{

    @Input() opcoes?: {titulo:string;valor:string|number}[] = []

    protected valor: string | number = null

    constructor( injector: Injector) {
        super(injector)
    }

    selecionar(event: any){
        console.log(event)
        this.valor = event
        this.onChange(this.valor);
        this.onTouched();
    }

}
