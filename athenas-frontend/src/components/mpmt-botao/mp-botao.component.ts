import {
    Component,
    EventEmitter,
    Input,
    OnChanges,
    OnInit,
    Output,
} from '@angular/core';

type COR =
    | 'primario'
    | 'secondario'
    | 'terciario'
    | 'branco'
    | 'successo'
    | 'critico';

type TIPO = 'preenchido' | 'borda';

/**
 */
@Component({
    selector: 'mpmt-botao',
    templateUrl: './mpmt-botao.component.html',
})
export class MpBotaoComponent implements OnInit, OnChanges {
    @Input() cor?: COR = 'primario';
    @Input() tipo?: TIPO = 'preenchido';
    @Input() isLoading?: boolean = false;
    @Output() readonly click?: EventEmitter<null> = new EventEmitter<null>();

    constructor() {
        this.ngOnChanges();
    }

    ngOnInit() {}

    ngOnChanges() {
        this.construirClasses();
    }

    construirClasses() {
        let classes = 'bg-primary text-white underscore';

        this.classes = classes;
    }

    classes = '';
}
