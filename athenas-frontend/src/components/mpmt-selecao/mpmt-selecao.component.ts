import {
    Component,
    EventEmitter,
    Input,
    OnChanges,
    OnInit,
    Output,
    ViewChild,
    forwardRef,
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import {
    MatAutocomplete,
    MatAutocompleteTrigger,
} from '@angular/material/autocomplete';
import {
    BehaviorSubject,
    debounceTime,
    map,
    Subject,
    Subscription,
    tap,
} from 'rxjs';
import { ehFuncao } from 'utils/eh-funcao';
import { ehString } from 'utils/eh-string';

export class MpmtSelecaoComponentConfiguracao {
    obterTitulo?: ((linha: any) => Promise<string>) | string;
    obterValor?: ((linha: any) => Promise<string>) | string;
    obterFiltros?: ((payload: any) => Promise<Object>) | Object;
    obterOpcoes?: (payload: any) => Promise<{ results: any[] }>;
}

@Component({
    selector: 'mpmt-selecao',
    templateUrl: './mpmt-selecao.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtSelecaoComponent),
            multi: true,
        },
    ],
    standalone: false
})
export class MpmtSelecaoComponent
    implements OnInit, OnChanges, ControlValueAccessor
{
    @Input() disabled?: boolean = false;
    @Input() titulo?: string = '';
    @Input() titulo_class?: string = '';
    @Input() placeholder?: string = 'Selecione';
    @Input() configuracao?: MpmtSelecaoComponentConfiguracao;
    @Output() onSelect: EventEmitter<any> = new EventEmitter<any>();

    private subscription: Subscription;
    private obterOpcoesSubject = new Subject();

    private opcoesSubject = new BehaviorSubject<
        { titulo: string; valor: string }[]
    >([]);
    private loadingSubject = new BehaviorSubject<boolean>(false);

    public opcoes$ = this.opcoesSubject.asObservable();
    public loading$ = this.loadingSubject.asObservable();

    public palavra_chave: string;
    public selecionado: any = undefined;
    public ativarSelecao = false;

    public isOptionsOpen = false;

    constructor() {}

    ngOnInit() {
        this.ativarSelecao = true;
    }

    ngOnDestroy() {
        this.subscription?.unsubscribe();
    }

    ngOnChanges(changes) {
        this.obterOpcoes();
    }

    ngAfterViewInit() {
        this.subscription = this.obterOpcoesSubject
            .pipe(debounceTime(1000))
            .subscribe((e) => {
                this.obterOpcoes();
            });
    }

    private async obterTitulo(linha: any) {
        const obterTitulo = this.configuracao.obterTitulo;

        if (!obterTitulo)
            return linha?.nome || linha?.titulo || linha?.descricao;

        if (ehString(obterTitulo)) return linha[obterTitulo as string];

        if (ehFuncao(obterTitulo))
            return await (obterTitulo as Function)(linha);

        return 'OPS....';
    }

    private async obterValor(linha: any) {
        const obterValor = this.configuracao.obterValor;

        if (!obterValor) return linha?.id || linha?.pk;

        if (ehString(obterValor)) return linha[obterValor as string];

        if (ehFuncao(obterValor)) return await (obterValor as Function)(linha);
    }

    private async obterFiltros(): Promise<((payload: any) => any[]) | Object> {
        if (typeof this.configuracao.obterFiltros === 'function') {
            return this.configuracao.obterFiltros({
                palavra_chave: this.palavra_chave,
            });
        } else {
            return { palavra_chave: this.palavra_chave };
        }
    }

    async mapear(linhas: any[]) {
        return Promise.all(
            linhas.map(async (linha) => {
                return {
                    titulo: await this.obterTitulo(linha),
                    valor: await this.obterValor(linha),
                };
            })
        );
    }

    private async obterOpcoes() {
        const filtros = await this.obterFiltros();

        const { obterOpcoes } = this.configuracao;
        let opcoes = [];
        if (obterOpcoes) {
            const response = await obterOpcoes(filtros);
            if (response && response.results) {
                opcoes = await this.mapear(response.results);
            } else {
                opcoes = [];
            }
        }

        this.opcoesSubject.next(opcoes);
    }

    public aplicarFiltros() {
        this.obterOpcoesSubject.next({});
    }

    public limparSelecao(): void {
        this.selecionado = undefined;
        this.onChange(undefined);
        this.aplicarFiltros();
    }

    public resetarSelecao(): void {
        this.selecionado = undefined;
        this.onChange(undefined);
        this.palavra_chave = '';
        this.aplicarFiltros();
    }

    public selecionar(opcao: any) {
        this.selecionado = opcao;
        if (this.mode == 'OBJECT') this.onChange(opcao);
        else this.onChange(opcao?.valor);

        this.onSelect.emit(opcao);
    }

    displayFn(opcao: any): string {
        // if (this.selecionado?.titulo) return this.selecionado?.titulo;
        // if (this.valor) return this.valor.toString();
        // if (opcao?.titulo) return opcao?.titulo;
        // return opcao;

        if (!opcao) return '';
        return opcao?.titulo?.replace(/<[^>]*>/g, '');
    }

    get multiple() {
        if (this.valor instanceof Array) return true;
        return false;
    }

    /** */
    mode: 'OBJECT' | 'PRIMITIVE';
    valor: string | number | boolean | object = '';
    onChange: any = () => {};
    onTouched: any = () => {};

    writeValue(value: string | any): void {
        this.mode ||= value === null ? 'PRIMITIVE' : undefined;
        this.mode ||= typeof value == 'object' ? 'OBJECT' : 'PRIMITIVE';
        if (this.mode == 'OBJECT') {
            this.selecionar({
                titulo: value?.titulo,
                valor: value?.valor,
            });
        } else {
            this.selecionar({
                titulo: value,
                valor: value,
            });
        }
        this.palavra_chave = value || '';
        this.valor = value;
        this.onChange(this.valor);
        this.obterOpcoesSubject.next({});
    }

    registerOnChange(fn: any): void {
        this.onChange = fn;
    }
    registerOnTouched(fn: any): void {
        this.onTouched = fn;
    }

    setDisabledState?(isDisabled: boolean): void {
        setTimeout(() => {
            this.disabled = isDisabled;
        }, 10);
    }

    onOptionsOpened() {
        this.isOptionsOpen = true; 
        this.bloquearInteracao(true);
    }

    onOptionsClosed() {
        this.isOptionsOpen = false;
        this.bloquearInteracao(false);
    }

    private bloquearInteracao(block: boolean) {
        if (block) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }
}
