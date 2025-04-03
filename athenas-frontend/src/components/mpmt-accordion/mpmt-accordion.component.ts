import { Component, Input, ContentChild, TemplateRef, OnInit } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MpmtColuna } from 'components/mpmt-celula/mpmt-celula.interface';
import { MpmtAccordionService } from './mpmt-accordion.service';


@Component({
    selector: 'mpmt-accordion',
    templateUrl: './mpmt-accordion.component.html',
    styleUrls: ['./mpmt-accordion.component.scss'],
    standalone: false
})
export class MpmtAccordionComponent implements OnInit {

    @Input('service') service: MpmtAccordionService;
    @Input('titulo') titulo: string;

    @Input('classe_titulo') classe_titulo: string;
    todasColunasItem: MpmtColuna[];
    todasColunasSubItem: MpmtColuna[];

    @ContentChild('acoesTemplate', { static: true }) acoesTemplate: TemplateRef<any>;
    @ContentChild('filtrosTemplate', { static: true }) filtrosTemplate: TemplateRef<any>;

    painelAberto: number = null;

    ngOnInit() {
        this.service.colunasItem$.subscribe((colunas) => {
            this.todasColunasItem = colunas;
        });

        this.service.colunasSubItem$.subscribe((colunas) => {
            this.todasColunasSubItem = colunas;
        });
    }

    toggleColunaVisivel(coluna: MpmtColuna) {
        coluna.visivel = !coluna.visivel;
        this.service.atualizarColunasVisiveisSubItem(this.todasColunasSubItem);
    }

    onPanelOpened(index: number): void {
        this.painelAberto = index;
    }

    onPanelClosed(index: number): void {
        this.painelAberto = null;
    }
    isPanelExpanded(index: number): boolean {

        return index === this.painelAberto;
        
      }
}
