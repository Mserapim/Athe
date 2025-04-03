import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiCoreChoicesFormulario } from 'api/core/api-core-choices-formulario.service';
import { apiDefinColaboradorEventualCriar } from 'api/defin/colaborador-eventual/api-defin-colaborador-eventual-criar.service';
import { apiDefinColaboradorEventualEditar } from 'api/defin/colaborador-eventual/api-defin-colaborador-eventual-editar.service';
import { apiDefinColaboradorEventual } from 'api/defin/colaborador-eventual/api-defin-colaborador-eventual.service';
import { apiRhLocations } from 'api/rh/api-rh-locations.service';
import { apiRhPaises } from 'api/rh/api-rh-paises';
import { apiRhEnderecolCriar } from 'api/rh/endereco/api-rh-endereco-criar.service';
import { apiRhEnderecolEditar } from 'api/rh/endereco/api-rh-endereco-editar.service';
import { apiRhEndereco } from 'api/rh/endereco/api-rh-endereco.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoFormComponent, MpmtSelecaoFormComponentConfiguracao } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';


class EnderecoModalComponentData {
    id?: number;
    pessoa_id?: number;
    orgao_id?: number;
    onClose?: Function;
}

@Component({
    selector: 'modal-endereco',
    templateUrl: './modal-endereco.component.html',
    styleUrls: ['./modal-endereco.component.scss'],
    standalone: false,
})
export class EnderecoModalComponent extends MpmtFormularioComponent<EnderecoModalComponentData> {



    modalButtons: ModalButton[] = [
        {
            label: 'Salvar',
            action: () => this.confirmarFormulario(),
            disabled: () => !this.formularioValido,
            color: 'white',
            backgroundColor: CoresPadraoEnum.verde
        }
    ];

    loading = true; // Variável de controle para o estado de carregamento

    protected formulario = new FormGroup({
        exterior: new FormControl<boolean>(false, [Validators.required]),
        tipo_logradouro: new FormControl<number>(null, [Validators.required]),
        tipo_endereco: new FormControl<number>(null, [Validators.required]),
        municipio: new FormControl<number>(null, [Validators.required]),
        logradouro: new FormControl<string>(null, [Validators.required]),
        numero: new FormControl<string>(null, [Validators.required]),
        complemento: new FormControl<string>(null, []),
        bairro: new FormControl<string>(null, [Validators.required]),
        cep: new FormControl<string>(null, [Validators.required]),
        pais: new FormControl<number>(null, []),
        cidade_exterior: new FormControl<string>(null, []),

    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: EnderecoModalComponentData,
        protected dialogRef: MatDialogRef<EnderecoModalComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
        protected dateAdapter: DateAdapter<Date>,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');

    }

    ngAfterViewInit() {
        this.loading = false;
    }

    ngOnInit() {
        this.carregarDados();

        this.formulario.get('exterior')?.valueChanges.subscribe((valor) => {
            if (valor) {
                // Se 'exterior' for true, torna 'pais' e 'cidade_exterior' obrigatórios
                this.formulario.get('pais')?.setValidators([Validators.required]);
                this.formulario.get('cidade_exterior')?.setValidators([Validators.required]);
                this.formulario.get('municipio')?.clearValidators();

                this.formulario.get('tipo_logradouro')?.setValue(100);

            } else {
                // Se 'exterior' for false, remove a obrigatoriedade
                this.formulario.get('pais')?.clearValidators();
                this.formulario.get('cidade_exterior')?.clearValidators();
                this.formulario.get('municipio')?.setValidators([Validators.required]);


            }

            // Atualiza os estados dos campos após modificar validadores
            // this.formulario.get('municipio')?.updateValueAndValidity();
            // this.formulario.get('pais')?.updateValueAndValidity();
            // this.formulario.get('cidade_exterior')?.updateValueAndValidity();
            // this.formulario.get('tipo_logradouro')?.updateValueAndValidity();
        });
    }


    async carregarDados() {
        if (this.data.id != null) {
            try {
                const response = await apiRhEndereco({
                    id: this.data.id,
                });

                await this.formulario.patchValue({
                    ...(response as any),

                });

            } catch (e) {
                console.error(e);
                this.exibirMensagem(
                    'Atenção',
                    'Erro inesperado ao carregar os valores do formulário'
                );
            }

        }
    }


    protected async confirmarFormulario() {
        try {

            const {
                exterior,
                tipo_logradouro,
                tipo_endereco,
                municipio,
                logradouro,
                numero,
                complemento,
                bairro,
                cep,
                pais,
                cidade_exterior,
            } = this.formulario.value;

            let orgao = this.data?.orgao_id
            let pessoa = this.data?.pessoa_id

            if (this.data?.id  == null ) {

                const result = await apiRhEnderecolCriar({
                    pessoa: pessoa,
                    orgao: orgao,
                    exterior: exterior,
                    tipo_logradouro: tipo_logradouro,
                    tipo_endereco: tipo_endereco,
                    municipio: municipio,
                    logradouro: logradouro,
                    numero: numero,
                    complemento: complemento,
                    bairro: bairro,
                    cep: cep,
                    pais: pais,
                    cidade_exterior: cidade_exterior,

                });

            } else {
                const result = await apiRhEnderecolEditar({
                    id: this.data.id,
                    pessoa: pessoa,
                    orgao: orgao,
                    exterior: exterior,
                    tipo_logradouro: tipo_logradouro,
                    tipo_endereco: tipo_endereco,
                    municipio: municipio,
                    logradouro: logradouro,
                    numero: numero,
                    complemento: complemento,
                    bairro: bairro,
                    cep: cep,
                    pais: pais,
                    cidade_exterior: cidade_exterior,

                });

            }
            this.fecharFormulario();
            this.data?.onClose();

        } catch (e: any) {
            console.error(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `${detalheErro}`;
            this.exibirMensagem('Aviso', texto);
        }
    }



    selecaoTipoEndereco: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiCoreChoicesFormulario,
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave, app: 'rh', name: 'TYPE_ADDRESS', per_page: 100 };
        },
        obterValor: 'valor',
        obterTitulo: 'display',
    };

    selecaoTipoLogradouro: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiCoreChoicesFormulario,
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave, app: 'rh', name: 'TYPE_STREET', per_page: 100 };
        },
        obterValor: 'valor',
        obterTitulo: 'display',
    };

    selecaoPais: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiRhPaises,
        obterFiltros: payload => {
            return { keyword: payload.palavra_chave, per_page: 100 };
        },
        obterValor: 'id',
        obterTitulo: 'nome',
    };

    selecaoMunicipio: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiRhLocations,
        obterFiltros: payload => {
            return { keyword: payload.palavra_chave, order_by:'nome' };
        },
        obterValor: 'id',
        obterTitulo: 'name',
    };



    endereco_exterior() {
        return this.formulario.get('exterior')?.value;
    }


}