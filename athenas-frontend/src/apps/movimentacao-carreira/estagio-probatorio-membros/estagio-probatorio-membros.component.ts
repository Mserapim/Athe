import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { EstagioProbatorioMembrosService } from './estagio-probatorio-membros.service';
import { AfastamentosComponent } from './afastamentos-estagio-probatorio/afastamentos-estagio-probatorio.component';

@Component({
    selector: 'estagio-probatorio-membros',
    templateUrl: 'estagio-probatorio-membros.component.html',
    standalone: false
})
export class EstagioProbatorioMembrosComponent implements OnInit {
    titulo = 'Membros em Estágio Probatório';

    constructor(
        public service: EstagioProbatorioMembrosService,
        public dialog: MatDialog
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'ID',
                visivel: false,
            },
            {
                codigo: 'matricula',
                titulo: 'Matricula',
                visivel: true,
            },
            {
                codigo: 'name',
                titulo: 'Nome',
                visivel: true,
            },
            {
                codigo: 'cargo',
                titulo: 'Cargo',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'data_primeira_posse',
                titulo: 'Primeira posse',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'data_exercicio',
                titulo: 'Data exercício',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'dias_trabalhados',
                titulo: 'Dias trabalhados',
                visivel: true,
            },
            {
                codigo: 'dias_afastados',
                titulo: 'Dias afastados',
                visivel: true,
            },
            {
                codigo: 'data_fim_estagio',
                titulo: 'Data final do estágio probatório',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'dias_para_fim_estagio',
                titulo: 'Dias para o estágio probatório',
                visivel: true,
            },
            {
                codigo: 'lotacao',
                titulo: 'Lotação',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        titulo: 'Ver afastamentos',
                        icone: 'grading',
                        aoClicar: (linha: any) => this.verAfastamentos(linha),
                    }
                ],
            },
        ]);
    }

    protected verAfastamentos(linha: { id: number }) {
        console.log(linha.id)
        this.dialog.open(AfastamentosComponent, {
            data: {
                membroId: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

}