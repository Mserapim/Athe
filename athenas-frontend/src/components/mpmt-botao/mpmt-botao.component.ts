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
    | 'sucesso'
    | 'critico'
    | 'destaque';

type TIPO = 'preenchido' | 'borda' | 'link';

/**
 */
@Component({
    selector: 'mpmt-botao',
    templateUrl: './mpmt-botao.component.html',
    styleUrls: ['./mpmt-botao.component.scss'],
    standalone: false
})
export class MpmtBotaoComponent implements OnInit, OnChanges {
    @Input() public cor?: COR = 'primario';
    @Input() public tipo?: TIPO = 'preenchido';
    @Input() public isLoading?: boolean = false;
    @Input() public desabilitado?: boolean = false;
    @Output() readonly click?: EventEmitter<null> = new EventEmitter<null>();

    classes = '';

    constructor() {
        this.ngOnChanges();
    }

    ngOnInit() {}

    ngOnChanges() {
        this.construirClasses();
    }

    construirClasses() {
        let classes = 'bg-primary text-white underscore';

        const cor = this.cor;
        const tipo = this.tipo;
        const desabilitado = this.desabilitado;

        const ehLink = tipo == 'link';
        const ehBorda = tipo == 'borda';
        const ehPreenchido = tipo == 'preenchido';

        const ehCorSucesso = cor == 'sucesso';
        const ehCorCritico = cor == 'critico';

        if (ehLink) classes = 'bg-transparent ';
        if (ehBorda) classes = 'bg-transparent outline outline-1 outline-black';
        if (ehPreenchido && ehCorSucesso) classes = 'text-white bg-[#00AC81]';
        if (ehPreenchido && ehCorCritico) classes = 'text-white bg-[#F87171]';
        if (ehPreenchido && cor == 'destaque')
            classes = 'text-white bg-[#C03437]';
        if (ehPreenchido && cor == 'branco') classes = 'text-black bg-white';
        if (ehPreenchido && desabilitado) classes = 'bg-gray-200 text-gray-800';

        if (!desabilitado) classes += ' cursor-pointer ';
        else classes += ' cursor-not-allowed ';

        if (this.isLoading) classes += ' opacity-80 cursor-not-allowed ';

        this.classes = classes;
    }

    public irClick(event) {
        if (this.desabilitado) return;
        if (this.isLoading) return;

        event?.stopPropagation();
        this.click.emit(event);
    }
}
