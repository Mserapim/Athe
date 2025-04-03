import { ChangeDetectorRef, Component, ElementRef, Input, OnInit, ViewChild, forwardRef } from '@angular/core';
import { FormControl, FormGroup, NG_VALUE_ACCESSOR, ControlValueAccessor } from '@angular/forms';
import { MatSelect } from '@angular/material/select';

export class MpmtSelecaoFormComponentConfiguracao {
    obterTitulo?: string;
    obterValor?: string;
    obterFiltros?: ((payload: any) => Promise<Object>) | Object;
    obterOpcoes?: (payload: any) => Promise<{ results: any[] }>;
}

interface Opcao {
    valor: number | string;
    titulo: string;
}

@Component({
    selector: 'mpmt-selecao-form',
    templateUrl: './mpmt-selecao-form.component.html',
    styleUrls: ['./mpmt-selecao-form.component.scss'],
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtSelecaoFormComponent),
            multi: true,
        },
    ],
    standalone: false
})
export class MpmtSelecaoFormComponent implements OnInit, ControlValueAccessor {
    form: FormGroup;
    opcoes: Opcao[] = []

    constructor(private cdr: ChangeDetectorRef) {}

    @Input() titulo?: string = '';
    @Input() titulo_class?: string = '';
    @Input() placeholder?: string = 'Pesquisar';
    @Input() configuracao?: MpmtSelecaoFormComponentConfiguracao;
    @Input() form_control?: FormControl;
    @Input() isReadOnly?: boolean = false;
    @Input() valor_display?: string = "";

    palavra_chave = "";
    tituloSelecionado: string = "";

    @ViewChild('selecaoOpcoes') selecaoOpcoes: MatSelect;
    @ViewChild('pesquisarInput', { static: false }) pesquisarInput: ElementRef;

    async ngOnInit() {
        this.form = new FormGroup({
            form_control: this.form_control
        });
 
        if (this.isReadOnly) {
            this.form.get('form_control').disable();
        } else {
            this.form.get('form_control').enable();
        }
 
        await this.obterOpcoes().then(() => {
            this.setarTituloInicial();
        });
    }

    ngAfterViewInit() {
        this.setar_valor_display()
        // if (this.form.get('form_control').value != null){
        //     this.setarSelecao(this.form.get('form_control').value);
        // }
    }

    private setar_valor_display(){

    }

    openSelect() {
        this.selecaoOpcoes.open();
    }

    private async obterTitulo(linha: any) {
        const obterTitulo = this.configuracao.obterTitulo;

        if (!obterTitulo)
            return linha?.nome || linha?.titulo || linha?.descricao;

        return linha[obterTitulo as string];

    }

    private async obterValor(linha: any) {
        const obterValor = this.configuracao.obterValor;

        if (!obterValor) return linha?.id || linha?.pk;

        return linha[obterValor];

    }

    private async obterFiltros(): Promise<((payload: any) => any[]) | Object> {
        if (typeof this.configuracao.obterFiltros === 'function') {
            return this.configuracao.obterFiltros({
                palavra_chave: this.palavra_chave,
            });
        } else {
            return {};
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

        if (obterOpcoes) {
            const response = await obterOpcoes(filtros);
            if (response && response.results) {
                this.opcoes = await this.mapear(response.results);
            } else {
                this.opcoes = [];
            }
        }
    }

    public aplicarFiltros(event: KeyboardEvent) {
        const inputElement = event.target as HTMLInputElement;
        this.palavra_chave = inputElement.value;
        this.obterOpcoes();
    }

    public async limparSelecao() {
        this.onChange(null);
        this.palavra_chave = '';
        await this.obterOpcoes();
        await this.setarTituloInicial();
    }

    public setarSelecao(valor: number | string) {
        this.onChange(valor);
        this.form.get('form_control').setValue(valor);
        this.palavra_chave = '';
    }

    public onSelectionChange(event: any) {
        const opcaoSelecionada = this.opcoes.find(opcao => opcao.valor === event.value);
        if (opcaoSelecionada) {
            this.tituloSelecionado = opcaoSelecionada.titulo; // Atualize o input com o título selecionado
        }
        this.pesquisarInput.nativeElement.value = this.tituloSelecionado; // Mostra o título no input
        this.onChange(event.value);
        this.form.get('form_control').setValue(event.value);
    }

    private async setarTituloInicial() {
        const valorSelecionado = this.form.get('form_control').value;
        if (valorSelecionado) {
          const opcaoSelecionada = this.opcoes.find(opcao => opcao.valor === valorSelecionado);
          if (opcaoSelecionada) {
            this.tituloSelecionado = opcaoSelecionada.titulo;
            this.pesquisarInput.nativeElement.value = this.tituloSelecionado; 

            this.cdr.detectChanges();
          }
        }
    }

    // ControlValueAccessor 
    value: string | number;
    onChange = (value: string | number) => { };
    onTouched = () => { };

    onInput(event: Event) {
        const input = event.target as HTMLInputElement;
        this.value = input.value;
        this.onChange(this.value);
    }

    writeValue(value: string | number): void {
        this.value = value;
    }

    registerOnChange(fn: (value: string | number) => void): void {
        this.onChange = fn;
    }

    registerOnTouched(fn: () => void): void {
        this.onTouched = fn;
    }

    setDisabledState?(isDisabled: boolean): void {
        if (isDisabled) {
            this.form.get('form_control').disable();
        } else {
            this.form.get('form_control').enable();
        }
    }
}
