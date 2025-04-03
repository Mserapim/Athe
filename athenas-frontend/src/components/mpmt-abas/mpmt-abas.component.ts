import { Component, Input, ViewChild, ViewContainerRef, AfterViewInit, ComponentRef, Type, Injector, ComponentFactoryResolver } from '@angular/core';

@Component({
    selector: 'mpmt-abas',
    templateUrl: './mpmt-abas.component.html',
    styleUrls: ['./mpmt-abas.component.scss'],
    standalone: false
})
export class MpmtAbasComponent implements AfterViewInit {
  @Input() tabs: any[];
  @Input() id: number;
  @ViewChild('conteudoDinamico', { read: ViewContainerRef }) conteudoDinamico: ViewContainerRef;
  private componentAtual: ComponentRef<any>;
  tabAtiva = 0;

  constructor(private injector: Injector) {}

  ngAfterViewInit() {
    this.carregarComponent(this.tabs[0]);
  }

  mudarTab(index: number) {
    this.tabAtiva = index;
    if (this.componentAtual) {
      this.componentAtual.destroy();
    }
    setTimeout(() => this.carregarComponent(this.tabs[index]), 0);
  }

  carregarComponent(tab: any) {
    if (this.conteudoDinamico) {
      this.conteudoDinamico.clear();
      const injector = Injector.create({
        providers: [
          { provide: 'data', useValue: tab.data },
        ],
        parent: this.injector
      });
      this.componentAtual = this.conteudoDinamico.createComponent(tab.component, { injector });
      if (this.componentAtual.instance.hasOwnProperty('id')) {
        this.componentAtual.instance.id = this.id;
      }
    } else {
      console.error('Falha ao carregar o componente: ViewContainerRef não disponível.');
    }
  }
}