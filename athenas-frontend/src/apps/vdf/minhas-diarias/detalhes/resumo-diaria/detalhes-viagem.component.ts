import { Component, Inject, Optional } from '@angular/core';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasViagem } from 'api/diarias/api-diarias-viagem.service';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { useGedDownload } from 'api/@base/use-ged-download';
import { VerDiariaService } from 'apps/diarias/gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.service';
import { printDate } from 'utils/print-date';

class DetalhesViagemComponentData {
    id: number;
}

@Component({
    selector: 'detalhes-viagem',
    templateUrl: './detalhes-viagem.component.html',
    styleUrls: ['../detalhes-diaria.component.scss'],
    standalone: false
})
export class DetalhesViagemComponent extends MpmtFormularioComponent<DetalhesViagemComponentData> {
    viagem: any = {};
    viagemOrigem: any = {};
    anexos: any = [];
    printDate = printDate;
    showTooltip = false;

    constructor(
        @Inject(MAT_DIALOG_DATA) protected data: DetalhesViagemComponentData,
        @Optional() protected dialogRef: MatDialogRef<DetalhesViagemComponentData>,
        protected snackBar: MatSnackBar,
        private verDiariaService: VerDiariaService
    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {
        super.ngOnInit();
        this.carregarDadosViagem().then(() => {
            if (this.viagem && this.viagem.viagem_origem) {
                this.carregarDadosViagemOrigem();
            }
        });
    }

    async carregarDadosViagem() {
        const id = this.data && this.data.id ? this.data.id : this.verDiariaService.viagemId;
        if (id != null) {
            try {
                const viagem = await apiDiariasViagem({ id: id });
                this.viagem = viagem;
                this.anexos = this.viagem.anexos;

                if (this.viagem.data_inicio_viagem) {
                    const [year, month, day] = this.viagem.data_inicio_viagem.split('-').map(Number);
                    this.verDiariaService.dataInicio = new Date(year, month - 1, day);
                }
                if (this.viagem.data_fim_viagem) {
                    const [year, month, day] = this.viagem.data_fim_viagem.split('-').map(Number);
                    this.verDiariaService.dataFim = new Date(year, month - 1, day);
                }
                if (this.viagem.situacao_etapa_atual) {
                    this.verDiariaService.fluxoViagem = this.viagem.situacao_etapa_atual;
                }
            } catch (e: any) {
                const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
                this.exibirMensagem('Erro', detalheErro);
            }
        }
    }

    async carregarDadosViagemOrigem() {
        const idOrigem = this.viagem.viagem_origem;
        if (idOrigem != null) {
            try {
                const viagemOrigem = await apiDiariasViagem({ id: idOrigem });
                this.viagemOrigem = viagemOrigem;

            } catch (e: any) {
                const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados da viagem de origem.';
                this.exibirMensagem('Erro', detalheErro);
            }
        }
    }

    protected exibirMensagem(titulo: string, texto: string) {
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar']
        });
    }

    public async downloadAnexo(id) {
        useGedDownload(id);
    }
}