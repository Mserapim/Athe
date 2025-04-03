import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleClasscodeCriar } from 'api/painel-controle/api-painel-controle-classcode-criar.service';
import { apiPainelControleTiposClasscode } from 'api/painel-controle/api-painel-controle-classcode-tipo.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

class PainelControleClasscodeNovoComponentData {
    onClose?: (classcode?: any) => void;
}

@Component({
    selector: 'painel-controle-classcode-novo',
    templateUrl: 'painel-controle-classcode-novo.component.html',
    standalone: false
})
export class PainelControleClasscodeNovoComponent extends MpmtFormularioComponent<PainelControleClasscodeNovoComponentData> {
    protected formulario = new FormGroup({
        slug: new FormControl<string>('', [Validators.required]),
        path: new FormControl<string>('', [Validators.required]),
        title: new FormControl<string>('', [Validators.required]),
        description: new FormControl<string>('', [Validators.required]),
        name_object: new FormControl<string>('', [Validators.required]),
        type_of: new FormControl<string>('', [Validators.required]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleClasscodeNovoComponentData,
        protected dialogRef: MatDialogRef<PainelControleClasscodeNovoComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
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
        return 'Novo classcode'
    }

    protected async resetarFormulario() {
        super.resetarFormulario();
    }

    protected async confirmarFormulario() {
        if (!this.validarFormulario()) return null;

        const { slug, path, title, description, name_object, type_of } = this.formulario.value;

        try {
            const response: any = await apiPainelControleClasscodeCriar({
                slug: slug,
                path: path,
                title: title,
                description: description,
                name_object: name_object,
                typeof: type_of.toUpperCase(),
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose(response.data);
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o classcode. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
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
