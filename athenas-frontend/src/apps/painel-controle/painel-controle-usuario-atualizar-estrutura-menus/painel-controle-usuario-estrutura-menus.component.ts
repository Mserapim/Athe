import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import {
    MAT_DIALOG_DATA,
    MatDialog,
} from '@angular/material/dialog';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';

import {FlatTreeControl} from '@angular/cdk/tree';
import {MatTreeFlatDataSource, MatTreeFlattener, MatTreeModule} from '@angular/material/tree';
import { PayloadEstruturaMenus, apiPainelControleControleAcessoUsurioEstruturaMenus } from 'api/painel-controle/api-painel-controle-controle-acesso-usuario-estrutura-menus.service';

export class PainelControleUsuarioEstrututaMenusComponentData {
    onClose?: Function;
    usuario?: any;
}


interface EstrutruraMenusItem {
    name: string;
    children?:EstrutruraMenusItem[]
}

interface FlatNode {
    expandable: boolean;
    name: string;
    level: number;
}


@Component({
    selector: 'painel-controle-usuario-estrutura-menus',
    templateUrl: 'painel-controle-usuario-estrutura-menus.component.html',
    standalone: false
})
export class PainelControleUsuarioEstruturaMenusComponent extends MpmtListagemComponent {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
    });

    private _transformer = (node: EstrutruraMenusItem, level: number) => {
        return {
          expandable: !!node.children && node.children.length > 0,
          name: node.name,
          level: level,
        };
      };
    
    treeControl = new FlatTreeControl<FlatNode>(
        node => node.level,
        node => node.expandable,
    );
    
    treeFlattener = new MatTreeFlattener(
        this._transformer,
        node => node.level,
        node => node.expandable,
        node => node.children,
    );

    dataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);

    constructor(
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleUsuarioEstrututaMenusComponentData,
    ) {
        super();
    }


    protected obterTitulo() {
        return 'Estrura Menus';
    }

    protected async obterColunas() {
        return {
            nome: 'Nome',
        };
    }

    protected async carregarEstruturaMenus(filtros:any) {
        return await apiPainelControleControleAcessoUsurioEstruturaMenus(filtros);

    }

    protected async configurarDados() {
        const response = await this.carregarEstruturaMenus(this.obterFiltroUsuario())
        this.dataSource.data = this.extractData(response.results);

    }

    protected extractData(data: any[]): EstrutruraMenusItem[] {
        return data.map(item => ({
            name: item.nome,
            children: item.grupos.map(grupo => ({
              name: grupo.nome,
              children: grupo.menus.map(menu => ({
                name: menu.nome
                }))
            }))
        }));
    }

    protected obterFiltroUsuario() {
        return<PayloadEstruturaMenus>{
            servidor_id:this.data.usuario.id
        }
    }

    hasChild = (_: number, node: FlatNode) => node.expandable;

   
}
