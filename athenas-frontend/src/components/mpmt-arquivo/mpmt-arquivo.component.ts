import { Component, Input, OnChanges, OnInit, forwardRef } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { useGedDownload } from 'api/@base/use-ged-download';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { BehaviorSubject, Subject, Subscription } from 'rxjs';

@Component({
    selector: 'mpmt-arquivo',
    templateUrl: './mpmt-arquivo.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtArquivoComponent),
            multi: true,
        },
    ],
    standalone: false
})
export class MpmtArquivoComponent
    implements OnInit, OnChanges, ControlValueAccessor
{
    @Input() disabled?: boolean = false;
    @Input() titulo?: string = '';
    @Input() titulo_class?: string = '';

    private subscription: Subscription;
    private obterOpcoesSubject = new Subject();

    private loadingSubject = new BehaviorSubject<boolean>(false);
    public loading$ = this.loadingSubject.asObservable();

    public arquivo: {
        valor?: number | string;
        display?: string;
    } = {};

    constructor() {}

    ngOnInit() {}

    ngOnDestroy() {
        this.subscription?.unsubscribe();
    }

    ngOnChanges(changes) {}

    ngAfterViewInit() {}

    async onFileInput($file) {
        const file = $file.target.files[0];
        const response = await gedUpload({
            file,
            fileName: file.name,
        });

        this.arquivo = { valor: response.data.file_id, display: file.name };
        if (typeof this.valor == 'object') this.valor = this.arquivo as any;
        else this.valor = this.arquivo?.valor as number;

        this.onChange(this.valor);
    }

    public async download() {
        useGedDownload(this.arquivoId?.toString());
    }

    get arquivoId() {
        if (typeof this.valor == 'object') return this.valor?.valor;
        else return this.valor;
    }

    /** */
    valor: number | { valor: number | string; display: string } = null;
    onChange: any = () => {};
    onTouched: any = () => {};

    writeValue(value: string | any): void {
        this.valor = value;
        if (typeof this.valor == 'object') {
            this.arquivo = this.valor || {};
            this.arquivo.display ||= 'Anexado';
        } else {
            this.valor = { valor: this.valor, display: 'Anexado' };
        }
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
}
