import { Component, Inject, Input, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { PublicacoesService } from './modal-publicacoes.component.service';
import { AnotacoesPessoaisPublicacaoNovoComponent } from 'apps/anotacoes-pessoais/anotacoes-pessoais-publicacao-novo/anotacoes-pessoais-publicacao-novo.component';
import { AnotacoesPessoaisPublicacaoEditarComponent } from 'apps/anotacoes-pessoais/anotacoes-pessoais-publicacao-editar/anotacoes-pessoais-publicacao-editar.component';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';


class ModalPublicacoesComponentData {
    selecionada?: number;
    onClose?: Function;
}


@Component({
    selector: 'modal-publicacoes',
    templateUrl: './modal-publicacoes.component.html',
    standalone: false
})
export class ModalPublicacoesComponent extends MpmtFormularioComponent<ModalPublicacoesComponentData> {

    protected titulo: string = "Publicações"

    protected formulario = new FormGroup({

    });
    
    protected get formularioValido() {
        return this.formulario.valid;
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: ModalPublicacoesComponentData,
        protected service: PublicacoesService,
        protected dialogRef: MatDialogRef<ModalPublicacoesComponentData>,
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
        this.service.carregarTiposPublicacao();

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
                codigo: 'cache_unicode',
                titulo: 'Título',
                visivel: true,
            },
            {
                codigo: 'tipo_display',
                titulo: 'Tipo de publicação',
                visivel: true,
            },
            {
                codigo: 'document',
                titulo: 'Documento',
                visivel: true,
            },
            {
                codigo: 'veiculo_publicacao_display',
                titulo: 'Veículo de publicação',
                visivel: true,
            },
            {
                codigo: 'data_vigencia',
                titulo: 'Data de vigência',
                visivel: true,
                tipo: 'DATA',
            },
            {
                codigo: 'data_publicacao',
                titulo: 'Data de publicação',
                visivel: true,
                tipo: 'DATA',

            },
            {
                codigo: 'import_siap',
                titulo: 'Importado do SIAP',
                visivel: false,
                tipo: 'BOLEANO_ICONE',
            },
            {
                codigo: 'created_by',
                titulo: 'Criado por',
                visivel: false,
            },
            {
                codigo: 'created_at',
                titulo: 'Criado em',
                visivel: false,
                tipo: 'DATA_HORA',
            },
            {
                codigo: 'modified_by',
                titulo: 'Modificado por',
                visivel: false,
            },
            {
                codigo: 'modified_at',
                titulo: 'Modificado em',
                visivel: false,
                tipo: 'DATA_HORA',

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
                ],
            },
        ]);

    }
    protected irNovo() {
        this.dialog.open(AnotacoesPessoaisPublicacaoNovoComponent, {
            data: {
                onClose: (publicacao) =>{ 
                    this.service.selecionada = publicacao.id;
                    this.service.recarregarListagem()
                },
            },
            width: '80%',
            height: '90%',
        });
    }

    protected irEditar(linha: any) {
        this.dialog.open(AnotacoesPessoaisPublicacaoEditarComponent, {
            data: {
                onClose: () => this.service.recarregarListagem(),
                id: linha.id,
            },
            width: '80%',
            height: '90%',
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
