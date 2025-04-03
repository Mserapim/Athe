import { Component, Inject, OnInit } from '@angular/core';
import { useGedDownload } from 'api/@base/use-ged-download';
import { BeneficiarioService } from '../beneficiario.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subscription } from 'rxjs';
import { apiDiariasPrestacoesContas } from 'api/diarias/prestacao-contas/api-diarias-prestacoes-contas.service';
import { apiReportDiariasPrestacaoContas } from 'api/report/api-report-diarias-prestacao-contas.service';

@Component({
    selector: 'prestacao-contas-diarias',
    templateUrl: './prestacao-contas-diarias.component.html',
    styleUrls: ['./prestacao-contas-diarias.component.scss'],
    standalone: false
})
export class PrestacoesContasDiariasComponent implements OnInit {

    prestacoes: any[] = [];
    viagem: any = {};



    protected snackBar: MatSnackBar;
    private subscriptions: Subscription = new Subscription();


    constructor(
        private beneficiarioService: BeneficiarioService,
        @Inject('data') private data: any
    ) {
    }

    ngOnInit() {
        this.subscriptions.add(
            this.beneficiarioService.beneficiarioIdAtual.subscribe(beneficiarioId => {
                if (beneficiarioId != null) {
                    this.carregarPrestacoesContaBeneficiario(beneficiarioId);
                }
            })
        );
    }

    ngOnDestroy() {
        this.subscriptions.unsubscribe();
    }

    async carregarPrestacoesContaBeneficiario(beneficiarioId: number) {      

        try {
            const data = await apiDiariasPrestacoesContas({beneficiario_id:beneficiarioId});
            this.prestacoes = data.results;
    
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }

    protected exibirMensagem(titulo: string, texto: string, classe: string = 'custom-snackbar') {
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }
    
    protected exibirErro(e: any) {
        const detalheErro = e?.response?.data?.message || '';
        const texto = `Ocorreu um erro inesperado ao salvar. ${detalheErro}`;
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar'],
        });
    }

    public async downloadAnexo(id) {
        useGedDownload(id);
    }

    protected async exportar_prestacao(id: number){
        try {
            const result =
                await apiReportDiariasPrestacaoContas({
                    id_prestacao: id,
                });

            this.exibirMensagem('', result.message, 'sucess-snackbar');
        } catch (e: any) {
            console.error(e);
            this.exibirErro(e);
        }
    }

}
