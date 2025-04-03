import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { useGedDownload } from 'api/@base/use-ged-download';
import { apiBeneficiarioDaaPassagem } from 'api/diarias/detalhe/api-diarias-daa-passagem.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DaaPassagemAereaData {
    destinoId: number;
    onClose?: Function;
}

@Component({
    selector: 'daa-passagem-aerea',
    templateUrl: 'daa-passagem-aerea.component.html',
    standalone: false
})
export class DaaPassagemAereaComponent extends MpmtFormularioComponent<DaaPassagemAereaData> implements OnInit {
    passagem: any = {};
    anexos: any[] = [];

    ngOnInit() {
        super.ngOnInit();
        this.carregarDadosPassagem();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DaaPassagemAereaData,
        protected dialogRef: MatDialogRef<DaaPassagemAereaData>,
        protected snackBar: MatSnackBar,
    ) {
        super(data, snackBar, dialogRef);
    }

    async carregarDadosPassagem() {
        if(this.data.destinoId != null) {
            try {
                const passagem = await apiBeneficiarioDaaPassagem({
                    destinoId: this.data.destinoId
                });

                this.passagem = passagem.results[0];
                this.anexos = this.passagem.anexos;

                const dataHoraBilhete = new Date(this.passagem.data_hora_bilhete);
                this.passagem.dataVoo = dataHoraBilhete.toLocaleDateString('pt-BR');
                this.passagem.horaSaidaVoo = dataHoraBilhete.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
            } catch (e: any) {
                const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
                this.exibirMensagem('Erro', detalheErro);
            }
        }
    }

    public async downloadAnexo(id) {
        useGedDownload(id);
    }

}
