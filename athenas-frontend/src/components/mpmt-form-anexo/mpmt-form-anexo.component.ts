import { Component, forwardRef, inject, Injector, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, NgControl } from '@angular/forms';
import { MpmtFormPadraoComponent } from 'components/mpmt-form-padrao/mpmt-form-padrao.component';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { useGedDownload } from 'api/@base/use-ged-download';
import { MessageService } from 'primeng/api';
import { gedUpload2 } from 'api/ged/api-ged-upload.service2';

export interface ArquivoAnexo {
    id: number | string;
    nome: string;
}

@Component({
    selector: 'mpmt-form-anexo',
    templateUrl: './mpmt-form-anexo.component.html',
    standalone: false,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtFormAnexoComponent),
            multi: true,
        },
    ],
})
export class MpmtFormAnexoComponent extends MpmtFormPadraoComponent<ArquivoAnexo>
    implements OnInit, OnChanges, ControlValueAccessor {

    @Input() formatosValidos?: string;

    protected valor: ArquivoAnexo = null;
    protected carregando = false;
    protected nomeArquivo = '';

    constructor(injector: Injector, private messageService: MessageService) {
        super(injector);
    }

    ngOnInit() {
        super.ngOnInit();
    }

    ngOnChanges(changes: SimpleChanges): void {
        super.ngOnChanges(changes);
    }

    /**
     */
    writeValue(value: ArquivoAnexo | null): void {
        this.valor = value;
        if (value && value.nome) {
            this.nomeArquivo = value.nome;
        } else {
            this.nomeArquivo = '';
        }
    }

    /**
     * Manipula o evento de seleção de arquivo
     */
    onFileSelect(event: Event): void {
        const fileInput = event.target as HTMLInputElement;
        if (fileInput.files && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            this.nomeArquivo = file.name;
            this.uploadArquivo(file);
        }
    }

    /**
     * Realiza o upload do arquivo para o servidor
     */
    async uploadArquivo(file: File): Promise<void> {
        try {

            
            this._mensagemDeErro = '';
            this.carregando = true;
            const response = await gedUpload2({
                fileName: file.name,
                file: file,
                // format_valid: this.formatosValidos
            });

            console.log(response)

            if (response?.file_id) {
                this.valor = {
                    id: response.file_id,
                    nome: file.name
                };
                this.onChange(this.valor);
                this.onTouched();
            } else {
                // Tratar erro de upload
                console.error('Erro ao fazer upload:', response?.message);
            }
        } catch (error) {
             this._mensagemDeErro = 'Erro ao fazer upload';
            console.error('Erro ao fazer upload:', error);
        } finally {
            this.carregando = false;
        }
    }

    /**
     * Remove o arquivo anexado
     */
    removerArquivo(): void {
        this.valor = null;
        this.nomeArquivo = '';
        this.onChange(this.valor);
        this.onTouched();
    }

    /**
     * Baixa o arquivo anexado
     */
    async baixarArquivo(): Promise<void> {
        if (this.valor && this.valor.id) {
            await useGedDownload(this.valor.id.toString());
        }
    }

    /**
     * Verifica se existe um arquivo anexado
     */
    get temArquivo(): boolean {
        return !!this.valor && !!this.valor.id;
    }


    _mensagemDeErro: string = '';
    mensagemDeErro(): string {
        if(this._mensagemDeErro) return this._mensagemDeErro;
        if (this.ngControl?.control?.errors?.required) {
          return 'Este campo é obrigatório.';
        }
    }
}
