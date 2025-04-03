import { Component, OnInit } from '@angular/core';
import { GestaoPessoasGestaoVdfVisualizarService } from './gestao-pessoas-gestao-vdf-visualizar.service';
import { DialogService } from 'primeng/dynamicdialog';
import { MpmtPaginaDialogoService } from 'components/mpmt-pagina-dialogo/mpmt-pagina-dialogo.service';

@Component({
    selector: 'gestao-pessoas-gestao-vdf-visualizar',
    templateUrl: 'gestao-pessoas-gestao-vdf-visualizar.component.html',
    standalone: false,
    providers: [DialogService],
})
export class GestaoPessoasGestaoVdfVisualizarComponent implements OnInit {

    constructor(
        public service: GestaoPessoasGestaoVdfVisualizarService, 
        private mpmtPaginaDialogoService: MpmtPaginaDialogoService
    ) {}

    ngOnInit() {}
    
    ngOnDestroy() {}

    abrir(payload: {solicitacaoId: string}){
        const ref = this.mpmtPaginaDialogoService.abrir(GestaoPessoasGestaoVdfVisualizarComponent);

        ref.onClose.subscribe((data: any) => {
            if (data) console.log(data)
        });
    }

    fechar(){
        this.mpmtPaginaDialogoService.fechar();
    }

    confirmar(){
        this.mpmtPaginaDialogoService.fechar();
    }
  
}