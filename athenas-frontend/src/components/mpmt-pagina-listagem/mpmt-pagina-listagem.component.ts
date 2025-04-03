import { Component, ContentChild, Input, OnDestroy, OnInit, TemplateRef } from '@angular/core';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { MpmtPaginaListagemColuna } from './mpmt-pagina-listagem.interface';
import { MpmtListagemService } from 'components/mpmt-listagens/mpmt-listagem.service';

@Component({
    selector: 'mpmt-pagina-listagem',
    templateUrl: './mpmt-pagina-listagem.component.html',
    standalone: false,
})
export class MpmtPaginaListagemComponent {

    @ContentChild('conteudoExpandido', { static: false }) conteudoExpandido!: TemplateRef<any>;
    @ContentChild('contentTemplate') contentTemplate: TemplateRef<any>;

    @Input('service') service: MpmtListagemService;
    @Input('ajuda-url') ajudaUrl?: string;
    @Input('ordenavel') ordenavel?: boolean;
    
    colunas: MpmtPaginaListagemColuna[];
    expandedRows = {};
    currentExpandedData: any;

    // Getter para verificar se o conteúdo expandido existe
    get temConteudoExpandido(): boolean {
        return !!this.conteudoExpandido;
    }

    constructor(public navegacaoAtualService: NavegacaoAtualService) {}

    /** links */
    abrirAjuda() {
        if (this.ajudaUrl) window.open(this.ajudaUrl, '_blank');
    }

    onRowExpand(event: any) {
        this.currentExpandedData = event.data;
    }

    onRowCollapse(event: any) {
        this.currentExpandedData = null;
    }
}
