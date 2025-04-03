import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MinhasDiariasService } from './minhas-diarias.service';
import { ActivatedRoute, Router } from '@angular/router';
import { DiariaStepperService } from '../stepper/diaria-stepper.service';
import { DetalhesDiariaComponent } from '../detalhes/detalhes-diaria.component';
import { DetalhesDiariaChefeImediatoComponent } from '../ciencia-chefe-imediato/ciencia-chefe-imediato.component';
import { CancelarDiariaComponent } from '../cancelar-diaria/cancelar-diaria.component';
import { ListaBeneficiariosDiariasComponent } from 'apps/diarias/gestao/viagem/ver-beneficiarios-diaria/ver-beneficiarios-diaria.component';

import { NgZone } from '@angular/core';
import { apiDiariaPermissao } from 'api/diarias/api-diaria-permissoes-diarias.service';

@Component({
    selector: 'minhas-diarias',
    templateUrl: 'minhas-diarias.component.html',
    styleUrls: ['./minhas-diarias.component.scss'],
    standalone: false
})
export class MinhasDiariasComponent implements OnInit {
    titulo = 'Minhas Diárias';
    currentUser: any;
    permissao = false;

    constructor(
        public service: MinhasDiariasService,
        public dialog: MatDialog,
        private router: Router,
        private stepperService: DiariaStepperService,
        private route: ActivatedRoute,
        private zone: NgZone
    ) {}

    ngOnInit() {
        this.service.carregarLinkAjuda();
        this.service.carregarUsuarioAtual().then(user => {
            this.currentUser = user;
            this.configurarColunas();
            this.service.recarregarListagem();
            this.service.carregarSituacoes();
            this.service.carregarMotivosViagem();
            this.service.carregarFinalidades();
        }).catch(error => {
            console.error('Erro ao carregar o usuário atual:', error);
        });
        this.service.carregarUsuarioAtual().then(user => {
            this.currentUser = user;
            this.configurarColunas();
            this.route.queryParams.subscribe(params => {
                const situacao = params['situacao'];
                if (situacao) {
                    const situacaoId = this.service.situacoes.find(s => s.descricao === situacao)?.id;
                    if (situacaoId) {
                        this.service.filtros.patchValue({ situacoes: [situacaoId] });
                    }
                }
                this.service.recarregarListagem();
            });
            this.service.recarregarListagem();
            this.service.carregarSituacoes();
            this.service.carregarMotivosViagem();
            this.service.carregarFinalidades();
        }).catch(error => {
            console.error('Erro ao carregar o usuário atual:', error);
        });
    }

    ngAfterViewInit(){
        this.carregarPermissao();
    }


    ngOnDestroy() {
        this.service.filtros.patchValue({ situacoes: null });
    }

    private async carregarPermissao() {
        try {
            const permissao = await apiDiariaPermissao();
            this.zone.run(() => {
                this.permissao = permissao;
            });
        } catch (error) {
            console.error('Erro ao carregar permissão:', error);
        }
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
                codigo: 'situacao_etapa_atual',
                titulo: 'Fluxo atual',
                ordenavel: false,
                visivel: true,
            },
            {
                codigo: 'solicitante',
                titulo: 'Solicitante',
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
                codigo: 'hospedagem_anfitriao',
                titulo: 'Hospedagem anfitrião',
                tipo: 'BOLEANO',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'finalidade_viagem_display',
                titulo: 'Finalidade',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'motivo_viagem_display',
                titulo: 'Motivo',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'tipo_viagem_display',
                titulo: 'Tipo',
                ordenavel: false,
                visivel: false,
            },
            {
                codigo: 'qtd_beneficiarios',
                titulo: 'Qtd. beneficiários',
                tipo: 'VER_MAIS',
                visivel: true,
                acoes: [
                    {
                        aoClicar: (linha: any) => this.irVerBeneficiarios(linha),
                    },
                ],
            },
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: false,
            },
            {
                codigo: 'acoes',
                tipo: 'ACAO_OU_ACOES_COM_DESTAQUE',
                ordenavel: false,
                visivel: true,
                acoes: [
                    {
                        titulo: 'Editar',
                        icone: 'edit',
                        aoClicar: (linha: any) => this.irEditarDiaria(linha),
                        exibirSe: (linha: any) => {return linha.situacao_solicitacao_display == "Rascunho" && this.permissao}
                    },
                    {
                        titulo: 'Cancelar',
                        icone: 'cancel',
                        aoClicar: (linha: any) => this.irCancelarDiaria(linha),
                        exibirSe: (linha: any) => this.exibirBotoesSolicitacao(linha.servidores_beneficiarios, linha.solicitante),
                    },
                    {
                        titulo: 'Ver detalhes',
                        icone: 'assignment',
                        aoClicar: (linha: any) => this.irVerDiaria(linha),
                        exibirSe: (linha: any) => this.exibirBotoesSolicitacao(linha.servidores_beneficiarios, linha.solicitante),
                    },
                    {
                        titulo: 'Dar ciência',
                        icone: 'assignment_turned_in',
                        icone_linha: true,
                        cor: (linha: any) => this.definirCorAcao(linha),
                        aoClicar: (linha: any) => this.irDarCiencia(linha),
                        exibirSe: (linha: any) => this.exibirBotaoDarCiencia(linha),
                    },
                ],
            },

        ]);
    }

    protected irNovaDiaria() {
        this.stepperService.id_viagem = null;
        this.router.navigate(['vdf/minhas-diarias/nova/diaria/step1']);
        
    }

    protected irEditarDiaria(linha: { id: number }) {
        this.stepperService.id_viagem = linha.id;
        this.router.navigate(['vdf/minhas-diarias/nova/diaria/step1']);

    }

    protected irCancelarDiaria(linha:any) {
        
        if (this.currentUser.id == linha.solicitante_servidor){
            this.cancelarDiariaSolicitante(linha.id)
        }
        else{
            this.cancelarDiariaBeneficiario(linha.id)
        }
    }

    protected cancelarDiariaBeneficiario(viagem_id: number ) {
        this.dialog.open(CancelarDiariaComponent, {
            data: {
                viagem_id: viagem_id,
                solicitante: false,
                currentUser: this.currentUser,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    };

    protected cancelarDiariaSolicitante( viagem_id ) {
        this.dialog.open(CancelarDiariaComponent, {
            data: {
                viagem_id: viagem_id,
                solicitante: true,
                currentUser: this.currentUser,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    };

    protected irVerDiaria(linha: { id: number }) {
        this.dialog.open(DetalhesDiariaComponent, {
            data: {
                id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
            width: '80%',
            height: '95%'
        });
    }

    protected irDarCiencia(linha: any) {
        this.dialog.open(DetalhesDiariaChefeImediatoComponent, {
            data: {
                id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
            width: '80%',
            height: '95%'
        });
    }

    public exibirBotaoDarCiencia(linha: any): boolean {
        if (!this.currentUser) {
            return false;
        }
        const chefesImediatos = linha.chefes_imediatos || [];
        const isChefeImediato = chefesImediatos.includes(this.currentUser.id);
        const mostrarDetalhes = this.exibirBotoesSolicitacao(linha.servidores_beneficiarios, linha.solicitante);

        // const condicao1 = isChefeImediato && linha.situacao_solicitacao_display !== "Rascunho";
        const condicao2 = isChefeImediato && linha.situacao_solicitacao_display === 'Aguardando ciência' && (linha.etapa_solicitacao_display === 'Chefe imediato' || linha.etapa_solicitacao_display === 'Chefe Imediato');
        // return condicao1 || condicao2;
        return condicao2
    }

    public definirCorAcao(linha: any): string {
        if (linha.situacao_solicitacao_display === 'Aguardando ciência' && linha.etapa_solicitacao_display === 'Chefe imediato') {
            return 'primary';
        } else {
            return '';
        }
    }

    public exibirBotoesSolicitacao(beneficiarios: number[], solicitante: string): boolean {
        if (!this.currentUser) {
            return false;
        }
        return (beneficiarios.includes(this.currentUser.id) || solicitante == this.currentUser.name)
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

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    protected get carregandoDados() {
        return this.service.carregando;
    }
    
}
