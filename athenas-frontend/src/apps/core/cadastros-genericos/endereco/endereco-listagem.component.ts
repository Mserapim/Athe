
import { Component, Input, OnInit } from '@angular/core';
import { EnderecoService } from './endereco-listagem.service';
import { EnderecoModalComponent } from './modal-endereco/modal-endereco.component';
import { MatDialog } from '@angular/material/dialog';
import { E } from '@angular/cdk/keycodes';

@Component({
    selector: 'endereco-listagem',
    templateUrl: 'endereco-listagem.component.html',
    styleUrls: ['endereco-listagem.component.scss'],
    standalone: false,
})
export class EnderecoListagemComponent implements OnInit {
    titulo = "endereços"

    @Input() pessoaId: number = null;
    @Input() orgaoId: number = null;
    @Input() cadastro: boolean = false;

    constructor(
        protected service: EnderecoService,
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
                codigo: 'unicode',
                titulo: 'Endereço Completo',
                visivel: true,
            },
            {
                codigo: 'municipio_display',
                titulo: 'Cidade',
                visivel: false,
            },
            {
                codigo: 'logradouro',
                titulo: 'Localidades',
                visivel: false,
            },
            {
                codigo: 'logradouro',
                titulo: 'Localidades',
                visivel: false,
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
        this.dialog.open(EnderecoModalComponent, {
            data: {
                onClose: () => { this.service.recarregarListagem() },
                pessoa_id: this.pessoaId,
                orgao_id: this.orgaoId,
            },
            width: '40%',
            height: '75%',
        });
    }

    irEditar(linha: any) {
        this.dialog.open(EnderecoModalComponent, {
            data: {
                onClose: () => { this.service.recarregarListagem() },
                pessoa_id: this.pessoaId,
                orgao_id: this.orgaoId,
                id: linha.id,
            },
            width: '40%',
            height: '75%',
        });
    }

}