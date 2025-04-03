import { ChangeDetectorRef, Component, Input, ViewChild } from '@angular/core';
import {
    MpmtPaginaListagemColuna,
    MpmtPaginaListagemLinha,
} from '../../mpmt-pagina-listagem.interface';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { MpmtPaginaListagemTabelaCelulaComponent } from '../mpmt-pagina-listagem-tabela-celula.component';
import { Popover } from 'primeng/popover';
import { BehaviorSubject, Subject } from 'rxjs';

@Component({
    selector: 'mpmt-pagina-listagem-tabela-celula-acoes',
    templateUrl: './mpmt-pagina-listagem-tabela-celula-acoes.component.html',
    standalone: false,
})
export class MpmtPaginaListagemTabelaCelulaAcoesComponent extends MpmtPaginaListagemTabelaCelulaComponent {
    @Input('coluna') coluna?: MpmtPaginaListagemColuna;
    @Input('linha') linha?: MpmtPaginaListagemLinha;

    constructor(public navegacaoAtualService: NavegacaoAtualService, 
        private cdr: ChangeDetectorRef,
    ) {
        super(navegacaoAtualService);
    }

    public items = [
        { label: 'Editar', icon: 'pi pi-pencil', command: () => alert(1) },
        { label: 'Excluir', icon: 'pi pi-trash', command: () => alert(2) }
      ];

    get opcoes(){

        return []
        //  (this.coluna?.acoes||[])?.map(acao => {
        //     const coluna = this.coluna;
        //     if(coluna.visivelSe && !coluna.visivelSe(this.linha)) return null;
        //     return {
        //         titulo: acao.titulo, 
        //         icone: acao.icone,
        //         requerPermissao: acao.requerPermissao,
        //         aoClicar: acao.aoClicar, 
        //     }
        // }).filter(Boolean)
    }

    @ViewChild('op') op!: Popover;

    selectedMember = null;

    members = [
        { name: 'Amy Elsner', image: 'amyelsner.png', email: 'amy@email.com', role: 'Owner' },
        { name: 'Bernardo Dominic', image: 'bernardodominic.png', email: 'bernardo@email.com', role: 'Editor' },
        { name: 'Ioni Bowcher', image: 'ionibowcher.png', email: 'ioni@email.com', role: 'Viewer' },
    ];

    aberto: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
    public aberto$ = this.aberto.asObservable()
    /**
     * Cancela as assinaturas (observables) para garantir que não haja
     * vazamentos de memória - (Memory Leaks).
     * Cancela a inscrição de todas as subscrições.
     */
    ngOnDestroy(): void {
        this.aberto.complete();
    }

    toggle(event) {

        console.log(event, this.aberto.value)
        this.aberto.next(!this.aberto.value);
        this.cdr.markForCheck();
    }



}
