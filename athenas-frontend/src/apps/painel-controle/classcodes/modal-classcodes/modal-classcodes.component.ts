import { Component, Inject, Input, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { ClasscodesService } from './modal-classcodes.component.service';
import { PainelControleClasscodeNovoComponent } from '../painel-controle-classcode-novo/painel-controle-classcode-novo.component';
import { PainelControleClasscodeEditarComponent } from '../painel-controle-classcode-editar/painel-controle-classcode-editar.component';
import { PainelControleClasscodeApagarComponent } from '../painel-controle-classcode-apagar/painel-controle-classcode-apagar.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

class ModalClasscodesComponentData {
    selecionada?: number;
    onClose?: Function;
}


@Component({
    selector: 'modal-classcodes',
    templateUrl: './modal-classcodes.component.html',
    standalone: false
})
export class ModalClasscodesComponent extends MpmtFormularioComponent<ModalClasscodesComponentData> {

    protected titulo: string = "Classcodes"

    protected formulario = new FormGroup({

    });
    
    protected get formularioValido() {
        return this.formulario.valid;
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: ModalClasscodesComponentData,
        protected service: ClasscodesService,
        protected dialogRef: MatDialogRef<ModalClasscodesComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
        public navegacaoAtualService: NavegacaoAtualService

    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {
        this.service.selecionada = this.data?.selecionada;
        this.configurarColunas();
        this.service.recarregarListagem();
        this.service.carregarTiposClasscode();
    }

    controlarTitulo(){
        return this.titulo
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'checkbox',
                titulo: '',
                visivel: true,
                tipo: 'RADIO',
                ordenavel: false,
            },
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: true,
            },
            {
                codigo: 'title',
                titulo: 'Título',
                visivel: true,
            },
            {
                codigo: 'path',
                titulo: 'Path',
                visivel: true,
            },
            {
                codigo: 'slug',
                titulo: 'Slug',
                visivel: false,
            },
            {
                codigo: 'name_object',
                titulo: 'Objeto',
                visivel: true,
            },
            {
                codigo: 'description',
                titulo: 'Descrição',
                visivel: true,
            },
            {
                codigo: 'typeof',
                titulo: 'Tipo',
                visivel: true,

            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                visivel: true,
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        requerPermissao: 'editar',
                        aoClicar: (linha: any) => this.irEditar(linha),
                    },
                    {
                        icone: 'delete',
                        titulo: 'Apagar',
                        requerPermissao: 'apagar',
                        aoClicar: (linha: any) => this.irApagar(linha),
                    },
                ],
            },
        ]);

    }

    modalButtons: ModalButton[] = [
        {
            label: 'Selecionar',
            action: () => this.confirmarFormulario(),
            disabled: () => !this.service.itemSelecionado,
            color: 'white',
            backgroundColor: CoresPadraoEnum.verde
        }
    ];

    protected irNovo() {
        this.dialog.open(PainelControleClasscodeNovoComponent, {
            data: {
                onClose: (classcode) =>{
                    this.service.selecionada = classcode.id;
                    this.service.recarregarListagem()
                },
            },
        });
    }

    protected irEditar(linha: any) {
        this.dialog.open(PainelControleClasscodeEditarComponent, {
            data: {
                onClose: () => this.service.recarregarListagem(),
                id: linha.id,
            },
        });
    }

    protected irApagar(linha: { id: number }) {
        this.dialog.open(PainelControleClasscodeApagarComponent, {
            data: {
                id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected async confirmarFormulario() {
        if (!this.service.itemSelecionado) return;
        let items = []
        try {
            this.fecharFormulario();
            items = this.service.obterItensSelecionados()
            this.data?.onClose(items[items.length-1]);

        } catch (e: any) {
            console.error(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }

    }
}
