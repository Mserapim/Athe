import { Component, EventEmitter, forwardRef, Injector, Input, OnChanges, OnInit, TemplateRef } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, NgControl } from '@angular/forms';
import { MpmtFormPadraoComponent } from 'components/mpmt-form-padrao/mpmt-form-padrao.component';

@Component({
    selector: 'mpmt-form-texto',
    templateUrl: './mpmt-form-texto.component.html',
    standalone: false,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtFormTextoComponent),
            multi: true,
        },
    ],
})
export class MpmtFormTextoComponent extends MpmtFormPadraoComponent<string>
implements OnInit, OnChanges, ControlValueAccessor {
 
    @Input() tipo: 'text' | 'password' | 'email' | 'number' = 'text';
    @Input() maxlength?: number;
    @Input() minlength?: number;
    @Input() iconePre?: string;
    @Input() iconePos?: string;
    @Input() iconPreTemplate?: TemplateRef<any>;
    @Input() iconPosTemplate?: TemplateRef<any>;
    
    protected valor: string | null = null;

    constructor(injector: Injector) {
        super(injector);
    }

    alterarValor(event: Event) {
        const input = event.target as HTMLInputElement;
        this.valor = input.value;
        this.onChange(this.valor);
        this.onTouched();
    }

    override mensagemDeErro(): string {
        if (this.ngControl?.control?.errors?.required) {
            return 'Este campo é obrigatório.';
        }
        if (this.ngControl?.control?.errors?.minlength) {
            return `O campo deve ter no mínimo ${this.minlength} caracteres.`;
        }
        if (this.ngControl?.control?.errors?.maxlength) {
            return `O campo deve ter no máximo ${this.maxlength} caracteres.`;
        }
        if (this.ngControl?.control?.errors?.email) {
            return 'O e-mail informado é inválido.';
        }
        return super.mensagemDeErro();
    }
}
