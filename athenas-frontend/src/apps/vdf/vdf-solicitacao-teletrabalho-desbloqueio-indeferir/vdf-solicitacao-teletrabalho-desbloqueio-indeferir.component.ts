import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import {
    MatDialogRef,
    MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FuseConfirmationService } from '@fuse/services/confirmation';
import { apiRhPvfApprovalsRequestsIdAuthorize } from 'api/rh/api-rh-pvf-approvals-requests-id-authorize.service';
import { apiRhPvfVendaSubstituicaoIdIndeferir } from 'api/rh/api-rh-pvf-venda-substituicao-id-indeferir.service';

export class VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirData {
    solicitacao_id: string | number;
}

@Component({
    selector: 'vdf-solicitacao-teletrabalho-desbloqueio-indeferir',
    templateUrl: 'vdf-solicitacao-teletrabalho-desbloqueio-indeferir.html',
    standalone: false
})
export class VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirComponent {
    observation: string = '';
    message: string;

    form = new FormGroup({
        teletrabalho_desbloqueio_data_encerramento: new FormControl<Date>(
            null,
            [Validators.required]
        ),
        teletrabalho_desbloqueio_prazo_impedimento: new FormControl<number>(0, [
            Validators.required,
        ]),
        teletrabalho_desbloqueio_anexo_id: new FormControl<{ valor: number }>(
            null,
            [Validators.required]
        ),
        observacao: new FormControl<string>('', [Validators.required]),
    });

    constructor(
        private _fuseConfirmationService: FuseConfirmationService,
        protected snackBar: MatSnackBar,
        private dialogRef: MatDialogRef<VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirData>,
        @Inject(MAT_DIALOG_DATA) public data: any
    ) {}

    fechar(): void {
        this.dialogRef.close();
    }

    protected irExecutarServico(linha: { id: number }) {

        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Tem certeza de que deseja indeferir esta solicitação? Essa ação não poderá ser desfeita.',
            icon: {
                show: true,
                name: 'heroicons_outline:exclamation',
                color: 'warn'
            },
            actions: {
                confirm: {
                    show: true,
                    label: 'Executar',
                    style: { 'background-color': '#dc2626' },                           
                },
                cancel: {
                    show: true,
                    label: 'Cancelar',
                    style: { 'background-color': '#cbd5e1' },
                }
            },
            dismissible: true
        });

        dialogRef.afterClosed().subscribe( async result => {
            if (result === 'confirmed') {
                try {
                    
                    result = await this.indeferir()
        
                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            }
        });
    }

    public async indeferir(): Promise<void> {
        this.message = null;
        try {
            const payload = {
                action: 'deny',
                requestId: this.data.solicitacao_id,
                observation: this.form.value.observacao || '',
                teletrabalho_desbloqueio_data_encerramento:
                    this.form.value.teletrabalho_desbloqueio_data_encerramento
                        .toISOString()
                        .substring(0, 10),
                teletrabalho_desbloqueio_prazo_impedimento:
                    this.form.value.teletrabalho_desbloqueio_prazo_impedimento,
                teletrabalho_desbloqueio_anexo_id:
                    this.form.value.teletrabalho_desbloqueio_anexo_id?.valor,
                anexos: [
                    this.form.value.teletrabalho_desbloqueio_anexo_id?.valor ||
                        undefined,
                ].filter((x) => x),
            };

            const response = await apiRhPvfApprovalsRequestsIdAuthorize(
                payload
            );

            this.dialogRef.close(response);
        } catch (e) {
            this.message = e?.response?.data?.message;
        }
    }

    protected exibirMensagem(
        titulo: string,
        texto: string,
        classe: string = 'custom-snackbar'
    ) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    gerarMeses() {
        return [
            { valor: 1, titulo: '1 mês' },
            { valor: 2, titulo: '2 mêses' },
            { valor: 3, titulo: '3 mêses' },
            { valor: 4, titulo: '4 mêses' },
            { valor: 5, titulo: '5 mêses' },
            { valor: 6, titulo: '6 mêses' },
            { valor: 7, titulo: '7 mêses' },
            { valor: 8, titulo: '8 mêses' },
            { valor: 9, titulo: '9 mêses' },
            { valor: 10, titulo: '10 mêses' },
            { valor: 11, titulo: '11 mêses' },
            { valor: 12, titulo: '1 ano' },
            { valor: 13, titulo: '1 ano e 1 mês' },
            { valor: 14, titulo: '1 ano e 2 mêses' },
            { valor: 15, titulo: '1 ano e 3 mêses' },
            { valor: 16, titulo: '1 ano e 4 mêses' },
            { valor: 17, titulo: '1 ano e 5 mêses' },
            { valor: 18, titulo: '1 ano e 6 mêses' },
            { valor: 19, titulo: '1 ano e 7 mêses' },
            { valor: 20, titulo: '1 ano e 8 mêses' },
            { valor: 21, titulo: '1 ano e 9 mêses' },
            { valor: 22, titulo: '1 ano e 10 mêses' },
            { valor: 23, titulo: '1 ano e 11 mêses' },
            { valor: 24, titulo: '2 anos' },
            { valor: 25, titulo: '2 anos e 1 mês' },
            { valor: 26, titulo: '2 anos e 2 mêses' },
            { valor: 27, titulo: '2 anos e 3 mêses' },
            { valor: 28, titulo: '2 anos e 4 mêses' },
            { valor: 29, titulo: '2 anos e 5 mêses' },
            { valor: 30, titulo: '2 anos e 6 mêses' },
            { valor: 31, titulo: '2 anos e 7 mêses' },
            { valor: 32, titulo: '2 anos e 8 mêses' },
            { valor: 33, titulo: '2 anos e 9 mêses' },
            { valor: 34, titulo: '2 anos e 10 mêses' },
            { valor: 35, titulo: '2 anos e 11 mêses' },
        ];
    }
}
