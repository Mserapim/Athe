import { Component, ContentChild, Input, TemplateRef } from '@angular/core';
import { MpmtPaginaListagemService } from '../mpmt-pagina-listagem.service';
import { MpmtPaginaListagemAcao, MpmtPaginaListagemLinha } from '../mpmt-pagina-listagem.interface';
import { combineLatest, map } from 'rxjs';
@Component({
    selector: 'mpmt-pagina-listagem-tabela',
    templateUrl: './mpmt-pagina-listagem-tabela.component.html',
    standalone: false,
})
export class MpmtPaginaListagemTabelaComponent {
    @ContentChild('conteudoExpandido2', { static: false }) conteudoExpandido2!: TemplateRef<any>;

    @Input('service') service?: MpmtPaginaListagemService;
    @Input('temConteudoExpandido') temConteudoExpandido = false;

    expandedRows = {};

    async customSort($event: any){
        if($event.order==1) this.service.ordenacao.order_by = $event.field
        else if($event.order==0)  this.service.ordenacao.order_by = undefined
        else this.service.ordenacao.order_by = `-${$event.field}`

        await this.service.recarregar();
    }

    items = [
        { label: 'New', icon: 'pi pi-plus' },
        { label: 'Search', icon: 'pi pi-search' }
    ];

    // selectedProduct: any | undefined;
    // displayProduct(event, product) {
    //     this.op.show(event);
    // }


    get permiteReordenarLinhas(){
        if(this.service.aoReordenarLinha) return true 
        return false
    }

    aoReordenarLinha($event: any){
        if(!this.permiteReordenarLinhas) return  
        this.service.aoReordenarLinha($event)
    }

    acoesVisiveisPorLinha(linha: MpmtPaginaListagemLinha) {
        return combineLatest([
            this.service.acoes$,
            this.service.listagem$
        ]).pipe(
            map(([acoes, linhas]) => {
                if (!linha) return acoes;
                return acoes.filter(acao => {
                    if (!acao.visivelSe) return true;
                    return acao.visivelSe(linha);
                });
            })
        );
    }

    aoClicarAcao(acao: MpmtPaginaListagemAcao, linha: MpmtPaginaListagemLinha){
        if(acao.aoClicar) acao.aoClicar(linha)
    }

    expandirTodasLinhas() {
        this.expandedRows  = this.service.listagemSubject.value.reduce((acc, p) => (acc[p.id] = true) && acc, {});        
    }

    colapsarTodasLinhas(){
        this.expandedRows = [];
    }

    get tabelaExpandida(){
        return Object.keys(this.expandedRows).length == this.service.listagemSubject.value.length
    }
}
