import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleClasscodeEditar } from 'api/painel-controle/api-painel-controle-classcode-editar.service';
import { apiPainelControleTiposClasscode } from 'api/painel-controle/api-painel-controle-classcode-tipo.service';
import { apiPainelControleClasscode } from 'api/painel-controle/api-painel-controle-classcode.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoFormComponent } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

class PainelControleClasscodeEditarComponentData {
    onClose?: Function;
    id: string;
}

@Component({
    selector: 'painel-controle-classcode-editar',
    templateUrl: 'painel-controle-classcode-editar.component.html',
    standalone: false
})
export class PainelControleClasscodeEditarComponent
    extends MpmtFormularioComponent<PainelControleClasscodeEditarComponentData>
    implements OnInit
{

    @ViewChild('selecaoTipo') selecaoTipo: MpmtSelecaoFormComponent;

    tipos: any[] = [];

    protected formulario = new FormGroup({
        id: new FormControl<string>('', []),
        slug: new FormControl<string>('', [Validators.required]),
        path: new FormControl<string>('', [Validators.required]),
        title: new FormControl<string>('', [Validators.required]),
        description: new FormControl<string>('', [Validators.required]),
        name_object: new FormControl<string>('', [Validators.required]),
        type_of: new FormControl<string>('', [Validators.required]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleClasscodeEditarComponentData,
        protected dialogRef: MatDialogRef<PainelControleClasscodeEditarComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
    }

    ngOnInit() {
        super.ngOnInit();
        this.carregarTipos();
    }
    
    modalButtons: ModalButton[] = [
        {
            label: 'Salvar',
            action: () => this.confirmarFormulario(),
            disabled: () => !this.formularioValido,
            color: 'white',
            backgroundColor: CoresPadraoEnum.verde
        }
    ];

    controlarTitulo() {
        return 'Editar classcode'
    }
    
    protected async resetarFormulario() {
        super.resetarFormulario();

        if (!this.data.id) return;

        try {
            const response = await apiPainelControleClasscode({
                id: this.data.id,
            });

            const classcode = response;

            await this.formulario.patchValue({
                ...(response as any),

                type_of: classcode.typeof,
            });
        } catch (e) {
            console.error(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os valores do formulário'
            );
        }
    }

    protected async confirmarFormulario() {
        if (!this.validarFormulario()) return null;

        const { id, slug, path, title, description, name_object } = this.formulario.value;

        const type_of = this.selecaoTipo.form_control.value;

        try {
            const response: any = await apiPainelControleClasscodeEditar({
                id: id,
                slug: slug,
                path: path,
                title: title,
                description: description,
                name_object: name_object,
                typeof: type_of,
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose(response.data);
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar. ${detalheErro}`;
            this.exibirMensagem('Atenção', texto);
        }
    }

    async carregarTipos() {
        try {
            const response = await this.selecaoTiposClasscode.obterOpcoes({});
            if (response && response.results) {
                this.tipos = response.results.map(item => ({
                    sigla: item.sigla,
                    texto: item.texto,
                }));
            }
        } catch (error) {
            console.error('Erro ao carregar os tipos:', error);
        }
    }

    selecaoTiposClasscode: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiPainelControleTiposClasscode,
        obterValor: 'sigla',
        obterTitulo: 'sigla',
    };

    validarFormulario(): boolean{
        let resposta = true
        if (!this.formulario.valid) resposta = false;

        if(!resposta){
            this.exibirMensagem('Aviso','Preencha todos os campos do formulário.')
        }

        return resposta;
    }
}
