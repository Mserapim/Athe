import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DiariasConfigCargosService } from './config-cargos.service';
import { DiariasConfigCargoNovoComponent } from '../config-cargo-novo/config-cargo-novo.component';
import { DiariasConfigCargoEditarComponent } from '../config-cargo-editar/config-cargo-editar.component';
import { DiariasConfigCargoApagarComponent } from '../config-cargo-apagar/config-cargo-apagar.component';
@Component({
    selector: 'config-cargos',
    templateUrl: 'config-cargos.component.html',
    standalone: false
})
export class DiariasConfigCargosComponent implements OnInit {
    titulo = 'Cargos';

    constructor(
        public service: DiariasConfigCargosService,
        public dialog: MatDialog
        
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'nome',
                titulo: 'Nome',
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        aoClicar: (linha: any) => this.irEditarCargo(linha),
                    },
                    {
                        icone: 'delete',
                        titulo: 'Apagar',
                        aoClicar: (linha: any) => this.irApagarCargo(linha),
                    },
                ],
            },
        ]);
    }

    protected irNovoCargo() {
        this.dialog.open(DiariasConfigCargoNovoComponent, {
            data: { onClose: () => this.service.recarregarListagem() },
        });
    }

    protected irEditarCargo(linha: { id: number }) {
        this.dialog.open(DiariasConfigCargoEditarComponent, {
            data: {
                id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected irApagarCargo(linha: { id: number }) {
        this.dialog.open(DiariasConfigCargoApagarComponent, {
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
