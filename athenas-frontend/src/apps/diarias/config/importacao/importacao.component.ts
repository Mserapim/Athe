import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DiariasConfigImportacaoService } from './importacao.service';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { apiRhSevidoresService } from 'api/rh/api-rh-servidores.service';
import { apiDiariasImportarSisdias } from 'api/diarias/api-diarias-importar-sisdias.service';
import { MatSnackBar } from '@angular/material/snack-bar';
@Component({
    selector: 'importacao',
    templateUrl: 'importacao.component.html',
    standalone: false
})
export class DiariasConfigImportacaoComponent implements OnInit {
    titulo = 'Importacao';

    constructor(
        public service: DiariasConfigImportacaoService,
        public dialog: MatDialog,
        protected snackBar: MatSnackBar,
 
    ) {}

    ngOnInit() {
      
    }

    selecaoServidor: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiRhSevidoresService,
        obterTitulo: (linha: any) => Promise.resolve(linha.matricula + " - " + linha.nome),
        obterValor: 'matricula',
        obterFiltros: payload => {
            return { 
                per_page: 50,
                page:1,
                palavra_chave: payload.palavra_chave,
            }; 
        },
    };


    
    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }



    protected async importarDados(){

        const filtros = this.service.filtros
        const result = await apiDiariasImportarSisdias(
            filtros?.value
        );
        const mensagem = result.message; 

        if (result.success){
            this.exibirMensagem('', mensagem, 'sucess-snackbar');
        }else{
            this.exibirErro(mensagem)
        }

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

    protected exibirErro(texto: string) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar'],
        });
    }


    limparSelecao(){
        this.service.filtros.reset();
    }


}
