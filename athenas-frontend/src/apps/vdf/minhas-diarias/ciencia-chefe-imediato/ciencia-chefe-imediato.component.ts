import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { VerDiariaService } from 'apps/diarias/gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.service';
import { ResumoBeneficiariosDiarias } from '../detalhes/beneficiarios/resumo-beneficiarios.component';
import { DetalhesViagemComponent } from '../detalhes/resumo-diaria/detalhes-viagem.component';


@Component({
    selector: 'ciencia-chefe-imediato',
    templateUrl: 'ciencia-chefe-imediato.component.html',
    standalone: false
})
export class DetalhesDiariaChefeImediatoComponent implements OnInit{
    public diariaId: number;
    dadosAbas = [];

    constructor(
        private dialogRef: MatDialogRef<DetalhesDiariaChefeImediatoComponent>,
        @Inject(MAT_DIALOG_DATA) public data: any,
        private verDiariaService: VerDiariaService,
    ) {}
    
    ngOnInit(): void {
        if (this.data && this.data.id) {
            this.diariaId = this.data.id;
            this.inicializarAbas();
        }
        this.verDiariaService.telaAprovador = false;
        this.verDiariaService.telaChefeImediato = true;
    }

    inicializarAbas() {
        this.dadosAbas = [
            { title: 'Diária', component: DetalhesViagemComponent, data: { diariaId: this.diariaId } },
            { title: 'Beneficiários', component: ResumoBeneficiariosDiarias, data: { diariaId: this.diariaId } },
        ];
    }

    onClose(): void {
        this.dialogRef.close();
    }
}
