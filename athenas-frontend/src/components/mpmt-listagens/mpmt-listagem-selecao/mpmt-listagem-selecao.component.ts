import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { tap } from 'rxjs';
import { MatCheckboxChange } from '@angular/material/checkbox';
import { MpmtListagemService } from '../mpmt-listagem.service';
import { MpmtColuna } from 'components/mpmt-celula/mpmt-celula.interface';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';

@Component({
    selector: 'mpmt-listagem-selecao',
    templateUrl: './mpmt-listagem-selecao.component.html',
    standalone: false
})
export class MpmtListagemSelecaoComponent implements OnInit {
  @Input('service') service: MpmtListagemService;
  @Input() permitirMultiplosSelecionados: boolean = true;  // Permitir múltiplas seleções por padrão
  @Input() tabelaComBorda: boolean = false;

  itensSelecionados = new Set<any>();
  todasColunas: MpmtColuna[];

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

    if (this.paginator) {
      this.service.colunas$.subscribe((colunas) => {
        this.todasColunas = colunas;
      });
    }

    // Assinar a listagem e selecionar o item após o carregamento dos dados
    this.service.listagem$.subscribe((itens) => {
      if (this.service?.selecionada&& itens.length > 0) {
        const item = this.obterItemPorId(this.service?.selecionada, itens);
        if (item) {
          this.service.adicionarItemSelecionado(item);
        }
      }
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

  toggleSelecao(element: any, event: MatCheckboxChange) {
    if (event.checked) {
      if (!this.permitirMultiplosSelecionados) {
        // Se apenas uma seleção for permitida, limpar as seleções anteriores
        this.service.limparItensSelecionados();
      }
      this.service.adicionarItemSelecionado(element);
    } else {
      this.service.removerItemSelecionado(element);
    }
  }

  estaSelecionada(element: any): boolean {
    return this.service.obterItensSelecionados().includes(element);
  }
  // Função para obter o item pelo ID da lista carregada
  obterItemPorId(id: any, itens: any[]): any {
    return itens.find(item => item.id === id);
  }
}

