import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { PainelControleHistoricoServicosService } from './painel-controle-historico-servicos.service';
import { ActivatedRoute } from '@angular/router';
import { ModalMensagensComponent } from '../modal-mensagens/modal-mensagens.component';

const EXECUTADO = [
    { value: 'True', label: 'Executado' },
    { value: 'False', label: 'Não executado' },
];

@Component({
    selector: 'painel-controle-historico-servicos',
    templateUrl: 'painel-controle-historico-servicos.component.html',
    standalone: false
})
export class PainelControleHistoricoServicosComponent implements OnInit {
    options = {
        executado: EXECUTADO,
    };

    titulo = 'Histórico de serviços';

    constructor(
        public service: PainelControleHistoricoServicosService,
        public dialog: MatDialog,
        private route: ActivatedRoute,
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.route.queryParams.subscribe(params => {
            const servico_id = params['servico_id'];
            if (servico_id) {
                this.service.filtros.patchValue({ servico_id: servico_id });
            }
        });
        this.service.recarregarListagem();
    }

    ngOnDestroy() {
        this.service.filtros.patchValue({ servico_id: null });
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: true,
            },
            {
                codigo: 'servico',
                titulo: 'Código serviço',
                visivel: false,
            },
            {
                codigo: 'nome',
                titulo: 'Nome',
                visivel: true,
            },
            {
                codigo: 'comando',
                titulo: 'Comando',
                visivel: true,
            },
            {
                codigo: 'classcode_path',
                titulo: 'Classcode',
                visivel: false,
            },
            {
                codigo: 'descricao',
                titulo: 'Descrição',
                visivel: true,
            },
            {
                codigo: 'ssid',
                titulo: 'SSID',
                visivel: true,
            },
            {
                codigo: 'executado_por_unicode',
                titulo: 'Executado por',
                visivel: true,
            },
            {
                codigo: 'iniciado_em',
                titulo: 'Iniciado em',
                visivel: true,
                tipo: 'DATA_HORA',
            },
            {
                codigo: 'finalizado_em',
                titulo: 'Finalizado em',
                visivel: true,
                tipo: 'DATA_HORA',
            },
            {
                codigo: 'execucao_unicode',
                titulo: 'Execução',
                visivel: true,
            },
            {
                codigo: 'sucesso',
                titulo: 'Sucesso',
                visivel: true,
                tipo: 'BOLEANO_ICONE',
            },            
            {
                codigo: 'created_at',
                titulo: 'Criado em',
                visivel: false,
                tipo: 'DATA_HORA',
            },
            {
                codigo: 'modified_at',
                titulo: 'Modificado em',
                visivel: false,
                tipo: 'DATA_HORA',
            },
            {
                codigo: 'created_by_unicode',
                titulo: 'Criado por',
                visivel: false,
            },
            {
                codigo: 'modified_by_unicode',
                titulo: 'Modificado por',
                visivel: false,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        icone: 'heroicons_outline:eye',
                        titulo: 'Visualizar',
                        requerPermissao: 'ler',
                        aoClicar: (linha: any) => this.irVisualizar(linha),
                    },
                ],
            },
        ]);
    }

    protected irVisualizar(linha: { id: number }) {
        this.dialog.open(ModalMensagensComponent, {
            data: {
                selecionada: linha.id,

                onClose: () => this.service.recarregarListagem(),
            },
            width: '80%',
            height: 'auto',
        });
    }

}
