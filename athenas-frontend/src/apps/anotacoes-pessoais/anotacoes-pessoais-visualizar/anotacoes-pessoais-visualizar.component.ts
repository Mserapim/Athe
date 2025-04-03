import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiAnotacoesPessoaisDetalhes } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-detalhes.service';
import { apiAnotacoesPessoaisTiposDocumentos } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-tipos-documentos.service';
import { apiAnotacaoPessoalTiposAnotacao } from 'api/anotacoes-pessoais/api-anotacoes-pessoal-minhas-anotacoes.service';
import {
    Bold,
    ClassicEditor,
    Essentials,
    Italic,
    Mention,
    Paragraph,
    Undo,
} from 'ckeditor5';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoComponent } from 'components/mpmt-selecao/mpmt-selecao.component';

class AnotacoesPessoaisVisualizarComponentData {
    anotacao_id: number;
    onClose?: Function;
}

@Component({
    selector: 'anotacoes-pessoais-visualizar',
    templateUrl: 'anotacoes-pessoais-visualizar.component.html',
    styles: [
        `
            input:read-only {
                opacity: 0.5;
            }

            input:-moz-read-only {
                /* For Firefox */
            }
        `,
    ],
    standalone: false
})
export class AnotacoesPessoaisVisualizarComponent extends MpmtFormularioComponent<AnotacoesPessoaisVisualizarComponentData> {
    @ViewChild('documentoTipoSelecao')
    documentoTipoSelecao: MpmtSelecaoComponent;

    protected formulario = new FormGroup({
        data_publicacao: new FormControl<string | Date>(null, []),
        documento_data: new FormControl<string>(''),
        documento_numero: new FormControl<string>(''),
        servidor: new FormControl<number>(null, [Validators.required]),
        documento_ano: new FormControl<string>('', [Validators.required]),
        documento_tipo: new FormControl<{
            titulo: string;
            valor: string;
        } | null>(null, [Validators.required]),
        tipo: new FormControl<{
            titulo: string;
            valor: string;
        } | null>(null, [Validators.required]),
        tipo_anotacao_id: new FormControl<number>(null),
        gedoc_numero: new FormControl<string>(''),
        servidor_matricula: new FormControl<string>(''),
        servidor_nome: new FormControl<string>(''),
        tipo_display: new FormControl<string>(''),
        publicacao: new FormControl<string>(''),
        publicacao_display: new FormControl<string>(''),
        data_efeito_inicio: new FormControl<string>(''),
        data_efeito_fim: new FormControl<string>(''),
        documento_tipo_display: new FormControl<string>(''),
        id: new FormControl<string>('', [Validators.required]),
        texto: new FormControl<string>('', [Validators.required]),
        textoAtualizado: new FormControl<string>(''),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: AnotacoesPessoaisVisualizarComponentData,
        protected dialogRef: MatDialogRef<AnotacoesPessoaisVisualizarComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>
    ) {
        super(data, snackBar, dialogRef);

        this.dateAdapter.setLocale('pt-BR');
    }

    title = '';

    public Editor = ClassicEditor;
    public config = {
        toolbar: ['undo', 'redo', '|', 'bold', 'italic'],
        plugins: [Bold, Essentials, Italic, Mention, Paragraph, Undo],
    };

    protected async resetarFormulario() {
        super.resetarFormulario();

        if (!this.data.anotacao_id) return;

        try {
            const response = await apiAnotacoesPessoaisDetalhes({
                id: this.data.anotacao_id,
            });

            await this.formulario.patchValue({
                ...(response as any),
                publicacao: response.publicacao || 'Não informado',
                data_publicacao: response.data_publicacao || 'Não informado',
                documento_tipo: {
                    valor: response.documento_tipo,
                    titulo: response.documento_tipo_display,
                } as any,
                tipo: {
                    valor: response.tipo,
                    titulo: response.tipo_display,
                } as any,
            });
        } catch (e) {
            console.log(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os valores do formulário'
            );
        }
    }

    protected async confirmarFormulario() {}

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];

    updateText($event) {
        const texto = $event?.editor?.getData();
        this.formulario.patchValue({
            textoAtualizado: texto,
        });
    }
}
