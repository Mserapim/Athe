import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { VerDiariaService } from './ver-diaria-aprovador.service';
import { DetalhesViagemComponent } from 'apps/vdf/minhas-diarias/detalhes/resumo-diaria/detalhes-viagem.component';
import { ResumoBeneficiariosDiarias } from 'apps/vdf/minhas-diarias/detalhes/beneficiarios/resumo-beneficiarios.component';
import { HistoricoDiariaComponent } from 'apps/vdf/minhas-diarias/detalhes/historico-diaria/historico-diaria.component';
import { Router } from '@angular/router';


@Component({
    selector: 'ver-diaria-aprovador',
    templateUrl: 'ver-diaria-aprovador.component.html',
    standalone: false
})
export class VerDiariaComponent implements OnInit{
    public diariaId: number;
    dadosAbas = [];

    constructor(
        private verDiariaService: VerDiariaService,
        protected router: Router,
        private cdr: ChangeDetectorRef,
    ) {}
    
    ngOnInit(): void {
        this.verDiariaService.viagemId$.subscribe(id => {
          if (id) {
            this.diariaId = id;
            this.inicializarAbas();
            this.cdr.detectChanges();
          }
        });
        this.verDiariaService.telaAprovador = true;
        this.verDiariaService.telaChefeImediato = false;
      }

    inicializarAbas() {
        this.dadosAbas = [
            { title: 'Diária', component: DetalhesViagemComponent, data: { diariaId: this.diariaId } },
            { title: 'Beneficiários', component: ResumoBeneficiariosDiarias, data: { diariaId: this.diariaId } },
            { title: 'Histórico', component: HistoricoDiariaComponent, data: { diariaId: this.diariaId } },
        ];
    }

    public irViagens() {
        this.verDiariaService.clearServiceData();
        this.router.navigate(['diarias/gestao/viagens']);
    }
}
