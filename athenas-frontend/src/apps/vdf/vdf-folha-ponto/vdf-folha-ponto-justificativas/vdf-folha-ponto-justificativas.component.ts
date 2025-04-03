import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { ViewEncapsulation } from '@angular/core';
import { VdfFolhaPontoJustificativasService } from './vdf-folha-ponto-justificativas.service';
import { VdfFolhaPontoJustificativaNovoComponent } from '../vdf-folha-ponto-justificativa-novo/vdf-folha-ponto-justificativa-novo.component';
import { apiFolhaPontoJustificativaCancelar } from 'api/folha-ponto/api-folha-ponto-justificativa-cancelar.service';
import { useGedDownload } from 'api/@base/use-ged-download';
import moment from 'moment';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { FuseConfirmationService } from '@fuse/services/confirmation';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';

export class VdfFolhaPontoJustificativasComponentData {
    onClose?: Function;
    filtros: {
        inicio?: Date;
        fim?: Date;
        ano?: number;
        mes?: number;
        servidor_id?: number;
    };
}

@Component({
    selector: 'vdf-folha-ponto-justificativas',
    templateUrl: 'vdf-folha-ponto-justificativas.component.html',
    encapsulation: ViewEncapsulation.None,
    standalone: false
})
export class VdfFolhaPontoJustificativasComponent implements OnInit {
    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: VdfFolhaPontoJustificativasComponentData,
        public service: VdfFolhaPontoJustificativasService,
        private _fuseConfirmationService: FuseConfirmationService,
        protected dialogRef: MatDialogRef<VdfFolhaPontoJustificativasComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
        private currentUserService: CurrentUserService
    ) {
        const filtros = data?.filtros;

        if (filtros) {
            this.service.filtros.reset();
            this.service.filtros.patchValue({
                ...filtros,
                servidor_id:
                    filtros.servidor_id ||
                    this.currentUserService.currentUser.id,
            });
        }
    }

    modalButtons: ModalButton[] = [
        {
            label: 'Incluir justificativa',
            action: () => this.irNovo(),
            color: 'white',
            backgroundColor: CoresPadraoEnum.azul
        }
    ];

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
        if (this.service.filtros.value.servidor_id) {
            this.service.obterServidorInfo(this.service.filtros.value.servidor_id)
        }
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                titulo: 'Motivo',
                codigo: 'tipo_justificativa_display',
                visivel: true,
            },
            {
                titulo: 'Data início',
                codigo: 'data_inicio',
                visivel: true,
                tipo: 'DATA',
            },
            {
                titulo: 'Data fim',
                codigo: 'data_fim',
                visivel: true,
                tipo: 'DATA',
            },
            {
                titulo: 'Qtd. horas',
                codigo: 'horas',
                visivel: true,
            },
            {
                titulo: 'Observações',
                codigo: 'observacao',
                visivel: true,
            },
            {
                titulo: 'Baixar',
                codigo: 'baixar',
                tipo: 'ICONE',
                transformarValor: () => 'heroicons_solid:paper-clip',
                aoClicar: (item: any) => this.download(item),
                visivel: true,
                exibirSe: (row) => row.anexo_id,
                construirEstilo: () => 'cursor-pointer',
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                visivel: true,
                acoes: [
                    {
                        icone: 'delete',
                        titulo: 'Excluir',
                        aoClicar: (linha: any) => this.irExcluir(linha),
                    },
                ],
            },
        ]);
    }

    async download(item) {
        try {
            await useGedDownload(item.anexo_id);
        } finally {
        }
    }

    async irExcluir(item) {
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Você tem certeza que deseja excluir essa justificativa?',
            icon: {
                show: true,
                name: 'heroicons_outline:exclamation',
                color: 'warn'
            },
            actions: {
                confirm: {
                    show: true,
                    label: 'Excluir',
                    style: { 'background-color': '#dc2626' },
                },
                cancel: {
                    show: true,
                    label: 'Cancelar',
                    style: { 'background-color': '#cbd5e1' },
                    useClass: true,
                    class: 'text-black'
                }
            },
            dismissible: true
        });
    
        dialogRef.afterClosed().subscribe(async (result) => {
            if (result === 'confirmed') {
                try {
                    const response = await apiFolhaPontoJustificativaCancelar({
                        justificativa_id: item.id,
                    });
    
                    this.exibirMensagem('', 'Justificativa excluída com sucesso.');
    
                    this.service.recarregarListagem();
                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || e?.response?.data?.datail || 'Erro ao excluir justificativa.';
                    this.exibirMensagem(
                        'Atenção',
                        detalheErro
                    );
                }
            }
        });
    }
    

    public irNovo() {
        const dialogRef = this.dialog.open(
            VdfFolhaPontoJustificativaNovoComponent,
            {
                data: {
                    ...this.data?.filtros,
                    close: () => {
                        dialogRef.close();
                    },
                },
            }
        );

        dialogRef.afterClosed().subscribe((result) => {
            this.service.recarregarListagem();
        });
    }

    printDate(d) {
        return moment(d).format('DD/MM/YYYY');
    }

    protected exibirMensagem(titulo: string, texto: string, classe: string = 'custom-snackbar') {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    protected fecharFormulario() {
        this.dialogRef.close();
        this.data.onClose();
    }
}
