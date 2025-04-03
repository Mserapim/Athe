import { Component, Input, OnInit } from '@angular/core';
import { SobreBeneficiarioComponent } from './sobre-beneficiario/sobre-beneficiario.component';
import { BeneficiarioService } from './beneficiario.service';
import { HistoricoBeneficiarioComponent } from './historico-beneficiario/historico-beneficiario.component';
import { TrechosDestinosBeneficiarioComponent } from './trechos-destinos/trechos-destinos.component';
import { LimiteDiariasComponent } from './limites-uso-diarias/limites-uso-diarias.component';
import { VerDiariaService } from 'apps/diarias/gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.service';


@Component({
    selector: 'detalhes-beneficiario',
    templateUrl: 'detalhes-beneficiario.component.html',
    styleUrls: ['./detalhes-beneficiario.component.scss'],
    standalone: false
})
export class DetalhesBeneficiariosComponent implements OnInit{
    @Input() beneficiarioId: number;
    @Input() telaAprovador: boolean;

    constructor(
        private beneficiarioService: BeneficiarioService,
        private verDiariaService: VerDiariaService
    ) {}
    
    dadosAbas = [];
    
    ngOnInit(): void {
        if (this.beneficiarioId) {
            this.beneficiarioService.atualizarBeneficiarioId(this.beneficiarioId);
            this.inicializarAbas();
        }
    }

    inicializarAbas() {
        this.dadosAbas = [
            { title: 'Beneficiário', component: SobreBeneficiarioComponent, data: { beneficiarioId: this.beneficiarioId } },
            { title: 'Trechos e destinos', component: TrechosDestinosBeneficiarioComponent, data: { beneficiarioId: this.beneficiarioId }},
            { title: 'Histórico', component: HistoricoBeneficiarioComponent, data: { beneficiarioId: this.beneficiarioId } },
        ];

        if (this.verDiariaService.telaAprovador) {
            this.dadosAbas.push({ title: 'Extrato de diárias', component: LimiteDiariasComponent, data: { beneficiarioId: this.beneficiarioId, extratoCompleto: true } });
        }
    }
}