import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ViagensService } from './viagens.service';
import { Router } from '@angular/router';
import { VerDiariaService } from './ver-diaria-aprovador/ver-diaria-aprovador.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { ListaBeneficiariosDiariasComponent } from './ver-beneficiarios-diaria/ver-beneficiarios-diaria.component';
import { MoverEtapaBeneficiarioComponent } from './ver-diaria-aprovador/analises-diaria/mover-etapa-especifica/mover-etapa-especifica.component';
import { apiDiariasChoicesMotivosViagem } from 'api/diarias/choices/api-diarias-motivos-viagem.service';
import { apiDiariasChoicesFinalidades } from 'api/diarias/choices/api-diarias-finalidades.service';
import { apiDiariasChoicesSituacoes } from 'api/diarias/choices/api-diarias-situacoes.service';
import { apiDiariasChoicesEtapas } from 'api/diarias/choices/api-diarias-etapas.service';


@Component({
    selector: 'viagens',
    templateUrl: 'viagens.component.html',
    standalone: false
})
export class ViagensComponent implements OnInit {
    titulo = 'Diárias';
    permissao = false

    apiDiariasChoicesMotivosViagem = apiDiariasChoicesMotivosViagem;
    apiDiariasChoicesFinalidades = apiDiariasChoicesFinalidades;
    apiDiariasChoicesSituacoes = apiDiariasChoicesSituacoes;
    apiDiariasChoicesEtapas = apiDiariasChoicesEtapas;

    constructor(
        protected currentUserService: CurrentUserService,
        public service: ViagensService,
        public dialog: MatDialog,
        private router: Router,
        private verDiariaService: VerDiariaService,
    ) {}

    ngOnInit() {
        
        this.currentUserService.load().then(() => {
            this.service.carregarPerfilAprovador(this.currentUserService?.currentUser?.id)
                .then(() => {
                    this.configurarColunas();
                });
        });

        this.service.recarregarListagem();

    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'data_solicitacao',
                titulo: 'Data da solicitação',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'solicitante',
                titulo: 'Solicitante',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'situacao_etapa_atual',
                titulo: 'Fluxo atual',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'data_inicio_viagem',
                titulo: 'Data início',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'data_fim_viagem',
                titulo: 'Data fim',
                tipo: 'DATA',
                visivel: true,
            },
            {
                codigo: 'qtd_beneficiarios',
                titulo: 'Beneficiários',
                tipo: 'VER_MAIS_DESTACADO',
                visivel: true,
                acoes: [
                    {
                        
                        aoClicar: (linha: any) => this.irVerBeneficiarios(linha),
                    },
                ],
            },
            {
                codigo: 'importada',
                titulo: 'Viagem importada',
                tipo: 'BOLEANO',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'possui_excedente',
                titulo: 'Possui excedente',
                tipo: 'BOLEANO',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'excedente',
                titulo: 'Viagem excedente',
                tipo: 'BOLEANO',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'motorista',
                titulo: 'Viagem de motorista',
                tipo: 'BOLEANO',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'recebido_por',
                titulo: 'Recebido por',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'tipo_viagem_display',
                titulo: 'Tipo viagem',
                ordenavel: false,
                visivel: false,
            },{
                codigo: 'motivo_viagem_display',
                titulo: 'Motivo viagem',
                ordenavel: false,
                visivel: false,
            },{
                codigo: 'finalidade_viagem_display',
                titulo: 'Finalidade da viagem',
                ordenavel: false,
                visivel: false,
            },{
                codigo: 'custeada_por_display',
                titulo: 'Custeada por',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'hospedagem_anfitriao',
                titulo: 'Hospedagem anfitrião',
                tipo: 'BOLEANO',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: false,
            },
            {
                codigo: '#',
                titulo: '',
                visivel: true,
                tipo: 'ICONE',
                width: '12px',
                tooltip: (linha: any) => 'Clique para mais informações',
                exibirSe: (linha: any) => (linha.link_informacao && this.verDiariaService.etapasAprovador.includes(linha.etapa_fluxo)),
                transformarValor: (linha: any) => 'help',
                aoClicar: (linha: any) => this.irAjuda(linha),
                construirEstilo: (linha: any) =>
                    'cursor-pointer text-blue-500',

            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        titulo: 'Ver solicitação',
                        icone: 'grading',
                        aoClicar: (linha: any) => this.irVerDiaria(linha),
                    },
                    {
                        titulo: 'Editar fluxo',
                        icone: 'edit',
                        aoClicar: (linha: any) => this.irEditarFluxoDiaria(linha),
                        exibirSe: (linha: any) => (this.service.perfil.grupos.includes('ADMIN')),
                    },
                    // {
                    //     titulo: 'Cancelar',
                    //     icone: 'cancel',
                    //     aoClicar: (linha: any) => this.irCancelarrDiaria(linha),
                    // },
                ],
            },
        ]);
    }

    protected irVerDiaria(linha: { id: number }) {
        this.verDiariaService.viagemId = linha.id;
        this.router.navigate(['diarias/gestao/viagens/viagem']);
    }
 

    protected irEditarFluxoDiaria(linha: { id: number }) {
        this.dialog.open(MoverEtapaBeneficiarioComponent, {
            data: {
                viagemId: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected irCancelarrDiaria(linha: { id: number }) {
        // this.dialog.open(PainelControleModuloEditarComponent, {
        //     data: {
        //         pk: linha.id,
        //         onClose: () => this.service.recarregarListagem(),
        //     },
        // });

        alert('em Construção');

    }

    irVerBeneficiarios(linha: { id: number }) {
        this.dialog.open(ListaBeneficiariosDiariasComponent, {
                data: {
                    id: linha.id,
                    onClose: () => this.service.recarregarListagem(),
                },
            }
        );
    }

    irAjuda(linha) {
        const url = linha.link_informacao;
        window.open(url, '_blank');
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }
}
