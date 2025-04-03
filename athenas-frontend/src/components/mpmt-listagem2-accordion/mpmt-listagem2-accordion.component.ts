import {Component, Input, OnInit, ViewChild} from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { tap } from 'rxjs';
import { MpmtListagem2AccordionService } from './mpmt-listagem2-accordion.service';
import { MpmtListagem2Coluna } from './mpmt-listagem2-accordion.interface';
import {NavegacaoAtualService} from "../../core/navegacao-atual/navegacao-atual.service";

@Component({
    selector: 'mpmt-listagem2-accordion',
    templateUrl: './mpmt-listagem2-accordion.component.html',
    styleUrls: ['./mpmt-listagem2-accordion.component.scss'],
    standalone: false
})
export class MpmtListagem2AccordionComponent implements OnInit {
    @Input('habilitar-favorito') habilitarFavorito: boolean = true;
    @Input('service') service: MpmtListagem2AccordionService;
    @Input('titulo') titulo: string;
    @Input('classe_titulo') classe_titulo: string;
    @Input('classes') classes: string = 'text-white';
    @Input('ocultarTitulo') ocultarTitulo: boolean = false;
    @Input('ocultarOpcoes') ocultarOpcoes: boolean = false;

    expandedElement: any | null;

    todasColunas: MpmtListagem2Coluna[];

    @ViewChild(MatPaginator) paginator: MatPaginator;

    acoes: { [key: string]: boolean } = {
        criar: false,
        editar: false,
        apagar: false,
        ler: false,
        download: false,
    };

    constructor(public navegacaoAtualService: NavegacaoAtualService) {}

    observarPermissoes() {
        this.navegacaoAtualService.acoes$.subscribe((acoes: string[]) => {
            if (!acoes) return;
            this.acoes = {};
            for (const acao of acoes) {
                this.acoes[acao] = acoes.includes(acao);
            }
        });
    }

    permite(acao: string) {
        return this.acoes[acao];
    }


    ngOnInit() {
        this.observarPermissoes();
        this.service.colunas$.subscribe((colunas) => {
            this.todasColunas = colunas;
        });
    }

    ngAfterViewInit() {
        if (this.paginator)
            this.paginator.page
                .pipe(
                    tap((x) => {
                        this.service.paginacao.page = 1 + (x.pageIndex || 0);
                        this.service.paginacao.per_page = x.pageSize || 10;
                        this.service.recarregarListagem();
                    })
                )
                .subscribe();
    }

    toggleColunaVisivel(coluna: MpmtListagem2Coluna) {
        coluna.visivel = !coluna.visivel;
        this.service.atualizarColunasVisiveis(this.todasColunas);
    }

    toggleRow(row: any, $event: MouseEvent) {
        this.expandedElement = this.expandedElement === row ? null : row;
    }

    isRowExpanded(row: any): boolean {
        if(this.expandedElement === row) {
            return true;
        }
        return false;
    }
}
