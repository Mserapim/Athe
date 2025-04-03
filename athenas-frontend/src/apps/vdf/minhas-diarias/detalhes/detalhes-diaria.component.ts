import { Component, Inject, OnInit } from '@angular/core';
import { DetalhesViagemComponent } from './resumo-diaria/detalhes-viagem.component';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { HistoricoDiariaComponent } from './historico-diaria/historico-diaria.component';
import { ResumoBeneficiariosDiarias } from './beneficiarios/resumo-beneficiarios.component';
import { VerDiariaService } from 'apps/diarias/gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.service';


@Component({
    selector: 'detalhes-diaria',
    templateUrl: 'detalhes-diaria.component.html',
    styleUrls: ['./detalhes-diaria.component.scss'],
    standalone: false
})
export class DetalhesDiariaComponent implements OnInit{
    public diariaId: number;
    dadosAbas = [];

    constructor(
        private dialogRef: MatDialogRef<DetalhesDiariaComponent>,
        @Inject(MAT_DIALOG_DATA) public data: any,
        private verDiariaService: VerDiariaService,
    ) {}
    
    ngOnInit(): void {
        this.verDiariaService.clearServiceData();
        
        if (this.data && this.data.id) {
            this.diariaId = this.data.id;
            this.inicializarAbas();
        }
        this.verDiariaService.telaAprovador = false;
        this.verDiariaService.telaChefeImediato = false;
    }

    inicializarAbas() {
        this.dadosAbas = [
            { title: 'Diária', component: DetalhesViagemComponent, data: { diariaId: this.diariaId } },
            { title: 'Beneficiários', component: ResumoBeneficiariosDiarias, data: { diariaId: this.diariaId } },
            { title: 'Histórico', component: HistoricoDiariaComponent, data: { diariaId: this.diariaId } },
        ];
    }

    onClose(): void {
        this.dialogRef.close();
    }
}
