import { Component, Inject, OnInit } from '@angular/core';
import {
    MAT_DIALOG_DATA,
    MatDialog,
    MatDialogRef,
} from '@angular/material/dialog';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import moment from 'moment';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DateAdapter } from '@angular/material/core';
import { MpmtAssinadorComponent } from 'apps/core/mpmt-assinador/mpmt-assinador.component';
import { apiGerarCnab } from 'api/diarias/pagamentos/api-gerar-cnab.service';
import { useGedDownload } from 'api/@base/use-ged-download';
import { ActivatedRoute, Router } from '@angular/router';

export class PagamentoCnabEmMassaCriarComponentData {
    titulo: string;
    dados: {
        id: number;
        servidor: string;
        valor_liquido_deferido_viagem: number;
        info_conta_bancaria: string;
    }[];
    onClose?: Function;
}

@Component({
    selector: 'cnab-multiplos-beneficiarios-criar',
    templateUrl: './cnab-multiplos-beneficiarios-criar.component.html',
    standalone: false,
})
export class PagamentoCnabEmMassaCriarComponent
    extends MpmtFormularioComponent<PagamentoCnabEmMassaCriarComponentData>
    implements OnInit
{
    displayedColumns: string[] = [
        'servidor',
        'valor_liquido_deferido_viagem',
        'info_conta_bancaria',
    ];
    protected formulario = new FormGroup({
        dataPagamento: new FormControl('', [
            Validators.required,
            this.validarData,
        ]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PagamentoCnabEmMassaCriarComponentData,
        protected dialogRef: MatDialogRef<PagamentoCnabEmMassaCriarComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
        private dialog: MatDialog,
        private router: Router,
        private route: ActivatedRoute
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
    }

    validarData(control: FormControl) {
        const dataSelecionada = moment(control.value);
        const hoje = moment().startOf('day');
        return dataSelecionada.isBefore(hoje) ? { dataRetroativa: true } : null;
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        this.dialog.open(MpmtAssinadorComponent, {
            data: {
                titulo: 'Assinatura necessária',
                onClose: (assinaturaData: any) => {
                    this.enviarDados(assinaturaData);
                },
            },
        });
    }

    private async enviarDados(assinaturaData: any) {
        const dataPagamento = moment(
            this.formulario.value.dataPagamento
        ).format('YYYY-MM-DD');

        const formData = {
            pgto_ids: this.data.dados.map((item) => item.id),
            data_pgto: dataPagamento,
            assinado_por: assinaturaData.usuario,
        };

        try {
            const response = await apiGerarCnab(formData);
            this.snackBar.open(response.message, '', {
                duration: 3000,
            });

            await this.downloadAnexo(response.file_id);

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (error) {
            console.error(error);
            this.snackBar.open('Erro ao gerar CNAB', '', {
                duration: 3000,
            });
        }
    }

    public async downloadAnexo(id: string) {
        useGedDownload(id);
    }

    protected fecharFormulario() {
        this.dialogRef.close();
        this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { beneficiarios: null },
            queryParamsHandling: 'merge',
        });
    }
}
