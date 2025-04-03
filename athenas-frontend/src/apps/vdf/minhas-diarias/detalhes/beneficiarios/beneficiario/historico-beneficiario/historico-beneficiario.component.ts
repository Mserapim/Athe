import { Component, OnInit } from "@angular/core";
import { MatSnackBar } from "@angular/material/snack-bar";
import { BeneficiarioService } from "../beneficiario.service";
import { apiDiariasDetalheBeneficiarioHistorico } from "api/diarias/detalhe/api-diarias-beneficiario-historico.service";
import { DiariaHistoricoDetalheComponent } from "../../../historico-diaria/historico-diaria-anexos-informacoes/historico-diaria-anexos-informacoes.component";
import { MatDialog } from "@angular/material/dialog";

@Component({
    selector: 'historico-beneficiario',
    templateUrl: 'historico-beneficiario.component.html',
    standalone: false
})
export class HistoricoBeneficiarioComponent implements OnInit {
    historico: any = [];
    protected snackBar: MatSnackBar;

    constructor(
        private beneficiarioService: BeneficiarioService,
        public dialog: MatDialog,
    ) {}

    ngOnInit() {
        this.beneficiarioService.beneficiarioIdAtual.subscribe(beneficiarioId => {
            if (beneficiarioId != null) {
                this.carregarHistoricoBeneficiario(beneficiarioId);
            }
        });
    }

    async carregarHistoricoBeneficiario(beneficiarioId: number) {
        try {
            const historico = await apiDiariasDetalheBeneficiarioHistorico({ beneficiario_id: beneficiarioId });
            this.historico = historico.results.map(item => ({
                ...item,
                acao_por: item.ação_por
            }));
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
            this.exibirMensagem('Erro', detalheErro);
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

    protected irDetalhesHistorico(historico: number) {
        this.dialog.open(DiariaHistoricoDetalheComponent, {
            data: { 
                historicoId: historico,
            },
        });
    }

    decisaoMap: { [key: string]: string } = {
        'deferido': 'Deferido',
        'indeferido': 'Indeferido',
        'encaminhado': 'Encaminhado',
        'ciente': 'Ciente do cancelamento',
        'valor_alterado': 'Valor deferido alterado',
        'importacao': 'Importação',
        'recebido': 'Recebido',
        'liberado': 'Liberado',
    };
}
