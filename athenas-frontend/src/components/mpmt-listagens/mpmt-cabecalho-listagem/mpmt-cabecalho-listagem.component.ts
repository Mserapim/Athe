import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { MpmtColuna } from 'components/mpmt-celula/mpmt-celula.interface';
import { MpmtListagemService } from '../mpmt-listagem.service';

@Component({
    selector: 'mpmt-cabecalho-listagem',
    templateUrl: './mpmt-cabecalho-listagem.component.html',
    standalone: false
})
export class MpmtCabecalhoListagemComponent implements OnInit {
    @Input('habilitar-favorito') habilitarFavorito: boolean = true;
    @Input('service') service: MpmtListagemService;
    @Input('titulo') titulo: string;
    @Input('classe_titulo') classe_titulo: string;
    @Input('classes') classes: string = 'text-white';
    @Input('ocultarTitulo') ocultarTitulo: boolean = false;
    @Input('ocultarOpcoes') ocultarOpcoes: boolean = false;

    todasColunas: MpmtColuna[];

    ngOnInit() {
        this.service.colunas$.subscribe((colunas) => {
            this.todasColunas = colunas;
        });
    }

    toggleColunaVisivel(coluna: MpmtColuna) {
        coluna.visivel = !coluna.visivel;
        this.service.atualizarColunasVisiveis(this.todasColunas);
    }
}