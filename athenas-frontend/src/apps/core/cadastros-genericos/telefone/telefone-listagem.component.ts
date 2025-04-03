
import { Component, Input, OnInit } from '@angular/core';
import { TelefoneService } from './telefone-listagem.service';
import { TelefoneModalComponent } from './modal-telefone/modal-telefone.component';
import { MatDialog } from '@angular/material/dialog';
import { E } from '@angular/cdk/keycodes';

@Component({
    selector: 'telefone-listagem',
    templateUrl: 'telefone-listagem.component.html',
    styleUrls: ['telefone-listagem.component.scss'],
    standalone: false,
})
export class TelefoneListagemComponent implements OnInit {
    titulo = "endereços"

    @Input() pessoaId: number = null;
    @Input() orgaoId: number = null;
    @Input() cadastro: boolean = false;

    constructor(
        protected service: TelefoneService,
        public dialog: MatDialog
    ) {
    }



    ngOnInit(): void {

        if (this.pessoaId || this.orgaoId) {
            if (this.pessoaId) {
                this.service.atualizarPessoaId(this.pessoaId);
            }
            else {
                this.service.atualizarOrgaoId(this.orgaoId);

            }
        }
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: false,
            },
            {
                codigo: 'tipo_telefone_display',
                titulo: 'Tipo Telefone',
                visivel: true,
            },
            {
                codigo: 'numero',
                titulo: 'Número',
                visivel: true,
            },
            {
                codigo: 'principal',
                titulo: 'Principal',
                visivel: true,
                tipo: 'BOLEANO_ICONE'
            },
            {
                codigo: 'publico',
                titulo: 'Publico',
                visivel: true,
                tipo: 'BOLEANO_ICONE'
            },

            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        titulo: 'Editar',
                        icone: 'edit',
                        aoClicar: (linha: any) => {
                            this.irEditar(linha)
                        },

                    },
                ],
            },
        ]);
    }

    irNovo() {
        this.dialog.open(TelefoneModalComponent, {
            data: {
                onClose: () => { this.service.recarregarListagem() },
                pessoa_id: this.pessoaId,
                orgao_id: this.orgaoId,
            },
            width: '600px',
            height: '450px',
        });
    }

    irEditar(linha: any) {
        this.dialog.open(TelefoneModalComponent, {
            data: {
                onClose: () => { this.service.recarregarListagem() },
                pessoa_id: this.pessoaId,
                orgao_id: this.orgaoId,
                id: linha.id,
            },
            width: '600px',
            height: '450px',
        });
    }

}