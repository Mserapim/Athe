import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { PainelControleConfigPontoService } from './painel-controle-configuracao-configuracao-de-ponto.service';
import { PainelControleConfigPontoCRUDComponent } from '../painel-controle-configuracao-configuracao-de-ponto-crud/painel-controle-configuracao-configuracao-de-ponto-crud.component';
import { apiPainelControleControleConfigPontoApagar } from 'api/painel-controle/api-painel-controle-configuracao-configuracao-de-ponto.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FuseConfirmationService } from '@fuse/services/confirmation';

@Component({
    selector: 'painel-controle-configuracao-configuracao-de-ponto',
    templateUrl: 'painel-controle-configuracao-configuracao-de-ponto.component.html',
    standalone: false
})
export class PainelControleConfigPontoComponent {
    titulo = 'Configuração de Ponto';

    constructor(
        public service: PainelControleConfigPontoService,
        public dialog: MatDialog,
        protected snackBar: MatSnackBar,
        private _fuseConfirmationService: FuseConfirmationService
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'place',
                titulo: 'Local',
                visivel: true,
            },
            {
                codigo: 'prosecution',
                titulo: 'Promotoria',
                visivel: true,
            },
            {
                codigo: 'network',
                titulo: 'Rede',
                visivel: true,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                visivel: true,
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        requerPermissao: 'editar',
                        aoClicar: (linha: any) => this.irEditarPonto(linha),
                    },
                    {
                        icone: 'delete',
                        titulo: 'Apagar',
                        requerPermissao: 'apagar',
                        aoClicar: (linha: any) => this.irApagarConfigPonto(linha),
                    },
                ],
            },
        ]);
    }

    protected irNovo() {
        this.dialog.open(PainelControleConfigPontoCRUDComponent, {
            data: { onClose: () => this.service.recarregarListagem() },
        });
    }

    protected irEditarPonto(linha: { id: number }) {
        this.dialog.open(PainelControleConfigPontoCRUDComponent, {
            data: {
                pk: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected exibirMensagem(
        titulo: string,
        texto: string,
        classe: string = 'custom-snackbar'
    ) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    protected irApagarConfigPonto(linha: { id: number }) {
        
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Você tem certeza que deseja remover o item selecionado ?',
            icon: {
              show: true,
              name: 'heroicons_outline:exclamation',
              color: 'warn'
            },
            actions: {
                confirm: {
                  show: true,
                  label: 'Apagar',
                  style: { 'background-color': '#dc2626' },                           
                },
                cancel: {
                  show: true,
                  label: 'Cancelar',
                  style: { 'background-color': '#cbd5e1' },
                }
              },
              dismissible: true
          });
      
          dialogRef.afterClosed().subscribe( async result => {
            if (result === 'confirmed') {
                try {
                    result = await apiPainelControleControleConfigPontoApagar({
                        id: linha.id
                    });
                    
                    this.exibirMensagem('', result.datail)
                    this.service.recarregarListagem()
        
                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            }
          });

    }

}
