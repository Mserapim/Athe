import { Component, Inject, OnInit } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { BeneficiarioService } from '../beneficiario.service';
import { apiDiariasLimiteUso } from 'api/diarias/detalhe/api-diarias-beneficiario-limite-uso.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { VerDiariaService } from 'apps/diarias/gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'limites-uso-diarias',
    templateUrl: './limites-uso-diarias.component.html',
    styleUrls: ['./limites-uso-diarias.component.scss'],
    standalone: false
})
export class LimiteDiariasComponent implements OnInit {
    extratoCompleto: boolean = false;
    tituloMesAno: string = '';
    limitesAnuais = [];
    limitesMensais = [];
    apenasUmMotivo = true;
    limites: any = {};
    viagem: any = {};

    ano: number;
    mesInicio: number;
    mesFim: number;

    protected snackBar: MatSnackBar;
    private subscriptions: Subscription = new Subscription();
    dataSource = new MatTableDataSource();
    displayedColumns: string[] = ['motivo', 'referencia', 'limite', 'usado', 'saldo'];

    constructor(
        private beneficiarioService: BeneficiarioService,
        private verDiariaService: VerDiariaService,
        @Inject('data') private data: any
    ) {
        this.extratoCompleto = data.extratoCompleto || false;
    }

    ngOnInit() {
        this.subscriptions.add(
            this.verDiariaService.dataInicio$.subscribe(dataInicio => {
                if (dataInicio) {
                    this.mesInicio = dataInicio.getMonth() + 1;
                    this.ano = dataInicio.getFullYear();
                }
            })
        );

        this.subscriptions.add(
            this.verDiariaService.dataFim$.subscribe(dataFim => {
                if (dataFim) {
                    this.mesFim = dataFim.getMonth() + 1;
                }
            })
        );

        this.subscriptions.add(
            this.beneficiarioService.beneficiarioIdAtual.subscribe(beneficiarioId => {
                if (beneficiarioId != null) {
                    this.carregarLimitesBeneficiario(beneficiarioId);
                }
            })
        );
    }

    ngOnDestroy() {
        this.subscriptions.unsubscribe();
    }

    async carregarLimitesBeneficiario(beneficiarioId: number) {      
        let meses: number[] = [this.mesInicio];

        if (this.mesInicio !== this.mesFim) {
            meses = [this.mesInicio, this.mesFim];
        }

        try {
            const parametros = { 
                beneficiario_id: beneficiarioId, 
                ano: this.ano
            };
    
            if (!this.extratoCompleto) {
                parametros['meses'] = meses;
            }
            const limites = await apiDiariasLimiteUso(parametros);
            this.limites = limites.results;
            this.processarLimites();
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }

    processarLimites() {
        this.limitesAnuais = [];
        this.limitesMensais = [];

        const todosMotivos = new Set();
        if (this.limites.mensal) {
            for (const mes in this.limites.mensal) {
                for (const motivo in this.limites.mensal[mes]) {
                    todosMotivos.add(this.limites.mensal[mes][motivo].motivos);
                    this.limitesMensais.push({
                        motivo: motivo,
                        referencia: `${mes}/${this.ano}`,
                        motivos: this.limites.mensal[mes][motivo].motivos,
                        limite: this.limites.mensal[mes][motivo].limite,
                        uso: this.limites.mensal[mes][motivo].uso,
                        saldo: this.limites.mensal[mes][motivo].saldo
                    });
                }
            }
        }
        this.apenasUmMotivo = todosMotivos.size === 1;

        if (this.limites.anual) {
            for (const motivo in this.limites.anual) {
                this.limitesAnuais.push({
                    motivo: motivo,
                    referencia: `${this.ano}`,
                    motivos: this.limites.anual[motivo].motivos,
                    limite: this.limites.anual[motivo].limite,
                    uso: this.limites.anual[motivo].uso,
                    saldo: this.limites.anual[motivo].limite - this.limites.anual[motivo].uso
                });
            }
        }

        this.limitesMensais.sort((a, b) => {
            const [mesA, anoA] = a.referencia.split('/').map(Number);
            const [mesB, anoB] = b.referencia.split('/').map(Number);
            return mesA - mesB || anoA - anoB;
        });

        this.dataSource.data = [...this.limitesMensais, ...this.limitesAnuais];
    }

    protected exibirMensagem(titulo: string, texto: string) {
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar']
        });
    }

    getMesNome(mes: string): string {
        const meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ];
        return meses[parseInt(mes, 10) - 1];
    }

}
