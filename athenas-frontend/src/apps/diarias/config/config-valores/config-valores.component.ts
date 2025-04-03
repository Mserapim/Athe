import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DiariasConfigValoresService } from './config-valores.service';
import { DiariasConfigValorNovoComponent } from '../config-valor-novo/config-valor-novo.component';
import { DiariasConfigValorEditarComponent } from '../config-valor-editar/config-valor-editar.component';
import { DiariasConfigValorApagarComponent } from '../config-valor-apagar/config-valor-apagar.component';
@Component({
    selector: 'config-Valores',
    templateUrl: 'config-valores.component.html',
    standalone: false
})
export class DiariasConfigValoresComponent implements OnInit {
    titulo = 'Valores';

    constructor(
        public service: DiariasConfigValoresService,
        public dialog: MatDialog
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'valor_estado',
                titulo: 'Valor estado',
            },
            {
                codigo: 'valor_fora_estado',
                titulo: 'Valor fora do estado',
            },
            {
                codigo: 'valor_exterior',
                titulo: 'Valor exterior',
            },
            {
                codigo: 'dt_inicio_vigencia',
                titulo: 'Início da vigência',
            },
            {
                codigo: 'dt_fim_vigencia',
                titulo: 'Fim da vigência',
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        aoClicar: (linha: any) => this.irEditarValor(linha),
                    },
                    {
                        icone: 'delete',
                        titulo: 'Apagar',
                        aoClicar: (linha: any) => this.irApagarValor(linha),
                    },
                ],
            },
        ]);
    }

    protected irNovoValor() {
        this.dialog.open(DiariasConfigValorNovoComponent, {
            data: { onClose: () => this.service.recarregarListagem() },
        });
    }

    protected irEditarValor(linha: { id: number }) {
        this.dialog.open(DiariasConfigValorEditarComponent, {
            data: {
                id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected irApagarValor(linha: { id: number }) {
        this.dialog.open(DiariasConfigValorApagarComponent, {
            data: {
                id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }
}
