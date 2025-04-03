import { Component, OnInit } from "@angular/core";
import { MatSnackBar } from "@angular/material/snack-bar";
import { apiDiariasBeneficiario } from "api/diarias/api-diarias-beneficiario.service";
import { BeneficiarioService } from "../beneficiario.service";
import { MatDialog } from "@angular/material/dialog";
import { DiariaAnaliseCeafComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/analise-diaria-ceaf/analise-diaria-ceaf.component";
import { VerDiariaService } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.service";
import { DiariaAnaliseDeplanEmpenhoComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/analises-diaria/analise-diaria-empenho-deplan/analise-diaria-deplan-empenho.component";
import { DiariaAnaliseDefinNotaComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/analises-diaria/analise-defin-nota-liquidacao/analise-defin-nota-liquidacao.component";
import { DiariaAnaliseDefinOrdemBancariaComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/analises-diaria/analise-defin-ordem-bancaria/analise-defin-ordem-bancaria.component";
import { apiBenecificarioCienciaChefeImediato } from "api/diarias/aprovacoes-beneficiario/ciencia-chefe-imediato.service";
import { DiariaInformacaoAprovadorComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/analises-diaria/informacao-e-aprovacao/informacao-e-aprovacao-diaria.component";
import { AprovarEditarNumeroDiariasComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/analises-diaria/aprovar-e-alterar-numero-diarias/aprovar-e-alterar-numero-diarias.component";
import { AnaliseAssessoriaDgDiariasComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/analises-diaria/analise-assessoria-dg/analise-assessoria-dg.component";
import { apiDiariasEventos } from "api/diarias/api-diarias-eventos.service";
import { AnaliseDefinExcedenteComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/analises-diaria/analise-defin-excedente/analise-defin-excedente.component";
import { apiDiariasExtrato } from "api/diarias/detalhe/api-extrato-diaria-beneficiario.service";
import { DiariaAssessoriaAfatsamentoPGJComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/analises-diaria/assessoria-pgj-afastamento/assessoria-pgj-afastamento.component";
import { apiObservacaoHistoricoFluxoBeneficiario } from "api/diarias/detalhe/api-historico-observacao-beneficiario.service";
import { EditarValorDeferidoDiariasComponent } from "./valor-liquido-deferido-editar/valor-liquido-deferido-editar.component";
import { apiReportDiariasOsConsolidada } from "api/report/api-report-diarias-os-consolidada.service";
import { apiBeneficiarioAnaliseDeplanCriar } from "api/diarias/analise-beneficiario/api-analise-deplan-empenho.service";
import { apiDiariasPerfilAprovador } from "api/diarias/config/grupo-aprovador/api-perfil-aprovador";
import { CurrentUserService } from "core/current-user/current-user.service";
import { apiDiariasBeneficiarioRecalcular } from "api/diarias/api-diarias-recalcular-beneficiario.service";
@Component({
    selector: 'sobre-beneficiario',
    templateUrl: './sobre-beneficiario.component.html',
    styleUrls: ['./sobre-beneficiario.component.scss'],
    standalone: false
})
export class SobreBeneficiarioComponent implements OnInit {
    loading: boolean = false;

    perfil: any = null;


    beneficiario: any = {};
    matricula: string = '';
    banco: string = '';
    agencia: string = '';
    conta: string = '';
    nome: string = '';
    feedback: string = '';

    eventos: any[] = [];
    extrato: any[] = [];

    analiseCeaf: boolean = false;
    analiseDeplan: boolean = false;
    analiseDeplanII: boolean = false;
    analiseDefinNota: boolean = false;
    analiseDefinOrdem: boolean = false;
    aprovacaoDG: boolean = false;
    liberacaoDG: boolean = false;
    aprovacaoSubAdm: boolean = false;
    analisePGJ: boolean = false;
    analiseSubJur: boolean = false;
    analiseAssessoriaPGJ: boolean = false;
    analiseAssessoriaSubJur: boolean = false;
    analiseAssessoriaSubJurII: boolean = false;
    analiseAssessoriaSubAdm: boolean = false;
    analiseAssessoriaSubAdmII: boolean = false;
    analiseAfastamentoAssessoriaPGJ: boolean = false;
    analiseAfastamentoPGJ: boolean = false;
    analiseAssessoriaDG: boolean = false;
    analiseAssessoriaDGII: boolean = false;
    analiseDefinExcedente: boolean = false;

    constructor(
        private beneficiarioService: BeneficiarioService,
        public verDiariaService: VerDiariaService,
        private snackBar: MatSnackBar,
        public dialog: MatDialog,
        protected currentUserService: CurrentUserService,
        
    ) {}

    ngOnInit() { 
        this.beneficiarioService.beneficiarioIdAtual.subscribe(async beneficiarioId => {
            if (beneficiarioId != null) {
                this.loading = true;
                try {
                    await this.carregarDadosBeneficiario(beneficiarioId);
                    await this.carregarEventosBeneficiario(beneficiarioId);
                    await this.carregarExtratoBeneficiario(beneficiarioId);
                    await this.carregarFeedbackAssessoria(beneficiarioId);
                } catch (error) {
                    console.error('Erro ao carregar dados do beneficiário:', error);
                } finally {
                    this.loading = false;
                }
            }
        });

        this.currentUserService.load().then(() => {
            this.carregarPerfilAprovador(this.currentUserService?.currentUser?.id)
        });
    }

    async carregarDadosBeneficiario(beneficiarioId: number) {
        try {
            const beneficiario = await apiDiariasBeneficiario({ id: beneficiarioId });
            this.beneficiario = beneficiario;
            if (this.beneficiario.conta_bancaria_unicode) {
                const parts = this.beneficiario.conta_bancaria_unicode.split(" - ");
                if (parts.length >= 3) {
                    this.banco = `${parts[0].trim()} - ${parts[1].trim()}`;
                    this.agencia = parts[2].trim();
                    this.conta = parts.length === 4 ? parts[3].trim() : '';
                }
            }
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }

    async carregarEventosBeneficiario(beneficiarioId: number) {
        try {
            const {results} = await apiDiariasEventos({ beneficiario: beneficiarioId });
            this.eventos = results;
            
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }

    async carregarExtratoBeneficiario(beneficiarioId: number) {
        try {
            const {results} = await apiDiariasExtrato({ beneficiario_id: beneficiarioId });
            this.extrato = results;
            
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }

    async carregarFeedbackAssessoria(beneficiarioId: number) {
        try {
            const payload = { beneficiario: beneficiarioId };
            const analise = await apiObservacaoHistoricoFluxoBeneficiario(payload);
            
            if (analise) {
            this.feedback = analise.feedback;
            }
        } catch (error) {
            console.error('Erro ao buscar a análise:', error);
        }
    }


    protected irAnalisar() {
        if (this.analiseCeaf) {
            const dialogRef = this.dialog.open(DiariaAnaliseCeafComponent, {
                data: {
                    beneficiario: this.beneficiario.id,
                    viagem: this.beneficiario.viagem,
                    onClose: () => {
                        this.carregarDadosBeneficiario(this.beneficiario.id);
                        this.refreshResumoBeneficiarios();
                    },
                },
                width: '80%',
            });
    
            dialogRef.afterClosed().subscribe(() => {
                this.refreshResumoBeneficiarios();
            });
        
        } else if (this.analiseDeplan || this.analiseDeplanII) {
            const exibirEncaminhar = this.analiseDeplan ? true : false;
            const dialogRef = this.dialog.open(DiariaAnaliseDeplanEmpenhoComponent, {
                data: {
                    beneficiario: this.beneficiario.id,
                    viagem: this.beneficiario.viagem,
                    exibirEncaminhar: exibirEncaminhar,
                    onClose: () => {
                        this.carregarDadosBeneficiario(this.beneficiario.id);
                        this.refreshResumoBeneficiarios();
                    },
                },
            });
    
            dialogRef.afterClosed().subscribe(() => {
                this.refreshResumoBeneficiarios();
            });
        
        } else if (this.analiseDefinNota) {
            const dialogRef = this.dialog.open(DiariaAnaliseDefinNotaComponent, {
                data: {
                    beneficiario: this.beneficiario.id,
                    viagem: this.beneficiario.viagem,
                    onClose: () => {
                        this.carregarDadosBeneficiario(this.beneficiario.id);
                        this.refreshResumoBeneficiarios();
                    },
                },
            });
    
            dialogRef.afterClosed().subscribe(() => {
                this.refreshResumoBeneficiarios();
            });
        
        } else if (this.analiseDefinOrdem) {
            const dialogRef = this.dialog.open(DiariaAnaliseDefinOrdemBancariaComponent, {
                data: {
                    beneficiario: this.beneficiario.id,
                    viagem: this.beneficiario.viagem,
                    onClose: () => {
                        this.carregarDadosBeneficiario(this.beneficiario.id);
                        this.refreshResumoBeneficiarios();
                    },
                },
            });
    
            dialogRef.afterClosed().subscribe(() => {
                this.refreshResumoBeneficiarios();
            });

        } else if (this.aprovacaoDG || this.aprovacaoSubAdm || this.analisePGJ || this.analiseSubJur 
            || this.analiseAfastamentoPGJ ) {
            
                let tituloModal: string;

            if (this.aprovacaoDG) {
                tituloModal = "Aguardando aprovador - DG";
            } else if (this.aprovacaoSubAdm) {
                tituloModal = "Aguardando aprovador - SUB ADM";
            } else if (this.analisePGJ) {
                tituloModal = "Aguardando análise - PGJ";
            } else if (this.analiseSubJur) {
                tituloModal = "Aguardando análise - SUB JUR";
            } else if (this.analiseAfastamentoAssessoriaPGJ) {
                tituloModal = "Análise afastamentos - Assessoria da PGJ";
            } else if (this.analiseAfastamentoPGJ) {
                tituloModal = "Análise afastamentos - Análise da PGJ";
            }
            const dialogRef = this.dialog.open(DiariaInformacaoAprovadorComponent, {
                data: {
                    beneficiario: this.beneficiario.id,
                    viagem: this.beneficiario.viagem,
                    titulo: tituloModal,
                    reanalise: this.beneficiario.reanalise,
                    onClose: () => {
                        this.carregarDadosBeneficiario(this.beneficiario.id);
                        this.refreshResumoBeneficiarios();
                    },
                },
            });
    
            dialogRef.afterClosed().subscribe(() => {
                this.refreshResumoBeneficiarios();
            });

        } else if (this.analiseAfastamentoAssessoriaPGJ) {
            const dialogRef = this.dialog.open(DiariaAssessoriaAfatsamentoPGJComponent, {
                data: {
                    beneficiario: this.beneficiario.id,
                    viagem: this.beneficiario.viagem,
                    titulo: "Análise afastamentos - Assessoria da PGJ",
                    onClose: () => {
                        this.carregarDadosBeneficiario(this.beneficiario.id);
                        this.refreshResumoBeneficiarios();
                    },
                },
            });
    
            dialogRef.afterClosed().subscribe(() => {
                this.refreshResumoBeneficiarios();
            });

        } else if (this.analiseAssessoriaPGJ || this.analiseAssessoriaSubJur || this.analiseAssessoriaSubAdm || 
            this.analiseAssessoriaSubJurII || this.analiseAssessoriaSubAdmII || this.analiseAssessoriaDGII) {
            let tituloModal: string;
            let encaminhar: boolean = false;

            if (this.analiseAssessoriaPGJ) {
                tituloModal = "Aguardando análise - Assessoria do PGJ";
            } else if (this.analiseAssessoriaSubJur) {
                tituloModal = "Aguardando análise - Assessoria do SUB JUR";
                encaminhar = true;
            } else if (this.analiseAssessoriaSubAdm) {
                tituloModal = "Aguardando análise - Assessoria da SUB ADM";
                encaminhar = this.beneficiario.categoria_funcional.includes("MEMBRO");
            } else if (this.analiseAssessoriaSubJurII) {
                tituloModal = "Aguardando análise - Assessoria do SUB JUR";
            } else if (this.analiseAssessoriaSubAdmII) {
                tituloModal = "Aguardando análise - Assessoria da SUB ADM";
            } else if (this.analiseAssessoriaSubAdmII) {
                tituloModal = "Aguardando análise - Assessoria da DG";
            }

            const dialogRef = this.dialog.open(AprovarEditarNumeroDiariasComponent, {
                data: {
                    beneficiario: this.beneficiario.id,
                    viagem: this.beneficiario.viagem,
                    titulo: tituloModal,
                    qtdTotalDiarias: this.beneficiario.qtd_total_diarias,
                    qtdTotalDiariasDeferidas: this.beneficiario.qtd_total_diarias_deferido,
                    excedente: this.beneficiario.codigo_os_viagem_original ? true : false,
                    possuiExcedente: this.beneficiario.codigo_os_excedente ? true : false,
                    encaminhar: encaminhar,
                    reanalise: this.beneficiario.reanalise,
                    onClose: () => {
                        this.carregarDadosBeneficiario(this.beneficiario.id);
                        this.refreshResumoBeneficiarios();
                    },
                },
            });
    
            dialogRef.afterClosed().subscribe(() => {
                this.refreshResumoBeneficiarios();
            });

        } else if (this.analiseAssessoriaDG) {
            const dialogRef = this.dialog.open(AnaliseAssessoriaDgDiariasComponent, {
                data: {
                    beneficiario: this.beneficiario.id,
                    titulo: "Aguardando análise - Assessoria da DG",
                    qtdTotalDiarias: this.beneficiario.qtd_total_diarias,
                    excedente: this.beneficiario.codigo_os_viagem_original ? true : false,
                    possuiExcedente: this.beneficiario.codigo_os_excedente ? true : false,
                    finalidadeAcompanhamento: this.verDiariaService.finalidadeAcompanhamento,
                    ehServidor: this.beneficiario.categoria_funcional.includes("SERVIDOR"),
                    onClose: () => {
                        this.carregarDadosBeneficiario(this.beneficiario.id);
                        this.refreshResumoBeneficiarios();
                    },
                },
                width: '80%',
            });
    
            dialogRef.afterClosed().subscribe(() => {
                this.refreshResumoBeneficiarios();
            });
        
        } else if (this.analiseDefinExcedente) {
            const dialogRef = this.dialog.open(AnaliseDefinExcedenteComponent, {
                data: {
                    beneficiario: this.beneficiario.id,
                    titulo: "Excedente - DEFIN",
                    qtdTotalDiarias: this.beneficiario.qtd_total_diarias,
                    onClose: () => {
                        this.carregarDadosBeneficiario(this.beneficiario.id);
                        this.refreshResumoBeneficiarios();
                    },
                },
            });
    
            dialogRef.afterClosed().subscribe(() => {
                this.refreshResumoBeneficiarios();
            });
        }
    }

    protected exibirBotaoAnalisar(): boolean {
        if (
            !this.verDiariaService.telaAprovador ||
            !this.compararFluxo(this.beneficiario.fluxo_unicode, this.verDiariaService.fluxoViagem) ||
            !this.verDiariaService.etapasAprovador.includes(this.beneficiario.etapa_fluxo)
        ) {
            return false;

        } else if (this.beneficiario.fluxo === 3) {  
            //Situação = "Aguardando análise", Etapa = "CEAF"
            this.analiseCeaf = true
            return true;

        } else if (this.beneficiario.fluxo === 50) {
            // Situação = "Empenho em andamento", Etapa = "DEPLAN - Executor"
            this.analiseDeplan = true
            return true;

        } else if (this.beneficiario.fluxo === 49) {
            // Situação = "Empenho em andamento", Etapa = "DEPLAN - Executor"
            this.analiseDeplanII = true
            return true

        } else if (this.beneficiario.fluxo === 47) {
            // Situação = "Aguardando nota liquidação", Etapa = "DEFIN - Gerência financeira"
            this.analiseDefinNota = true
            return true;

        } else if (this.beneficiario.fluxo === 51) {
            // Situação = "Ordem bancária em andamento", Etapa = "DEFIN - Gerência financeira"
            this.analiseDefinOrdem = true
            return true;

        } else if (this.beneficiario.fluxo === 7 || this.beneficiario.fluxo === 45) {
            // Situação = "Aguardando aprovador", Etapa = "DG"
            this.aprovacaoDG = true;
            return true;
        
        } else if (this.beneficiario.fluxo === 5 || this.beneficiario.fluxo === 37 || this.beneficiario.fluxo === 39) {
            // Situação = "Aguardando aprovador", Etapa = "SUB ADM"
            this.aprovacaoSubAdm = true;
            return true;

        } else if (this.beneficiario.fluxo === 23 || this.beneficiario.fluxo === 43) {
            // Situação = "Aguardando análise", Etapa = "PGJ"
            this.analisePGJ = true;
            return true;
        
        } else if (this.beneficiario.fluxo === 22 || this.beneficiario.fluxo === 36 || this.beneficiario.fluxo === 41) {
            // Situação = "Aguardando análise", Etapa = "SUB JUR"
            this.analiseSubJur = true;
            return true;

        } else if (this.beneficiario.fluxo === 28 || this.beneficiario.fluxo === 42) {
            // Situação = "Aguardando análise", Etapa = "Assessoria do PGJ"
            this.analiseAssessoriaPGJ = true;
            return true;

        }  else if (this.beneficiario.fluxo === 24) {
            // Situação = "Aguardando análise", Etapa = "Assessoria do SUB JUR"
            this.analiseAssessoriaSubJur = true;
            return true;
        
        }  else if (this.beneficiario.fluxo === 30 || this.beneficiario.fluxo === 40) {
            // Situação = "Aguardando análise", Etapa = "Assessoria do SUB JUR"
            this.analiseAssessoriaSubJurII = true;
            return true;

        }  else if (this.beneficiario.fluxo === 33) {
            // Situação = "Aguardando análise", Etapa = "Assessoria da SUB ADM"
            this.analiseAssessoriaSubAdm = true;
            return true;
        
        }  else if (this.beneficiario.fluxo === 31 || this.beneficiario.fluxo === 38) {
            // Situação = "Aguardando análise", Etapa = "Assessoria da SUB ADM"
            this.analiseAssessoriaSubAdmII = true;
            return true;
        
        }  else if (this.beneficiario.fluxo === 29) {
            // Situação = "Análise afastamentos", Etapa = "Assessoria da PGJ"
            this.analiseAfastamentoAssessoriaPGJ = true;
            return true;

        }  else if (this.beneficiario.fluxo === 6) {
            // Situação = "Aguardando análise", Etapa = "Assessoria da DG"
            this.analiseAssessoriaDG = true;
            return true;

        }  else if (this.beneficiario.fluxo === 44) {
            // Situação = "Aguardando análise", Etapa = "Assessoria da DG"
            this.analiseAssessoriaDGII = true;
            return true;

        }  else if (this.beneficiario.fluxo === 26) {
            // Situação = "Análise afastamentos", Etapa = "Análise da PGJ"
            this.analiseAfastamentoPGJ = true;
            return true;

        } else if (this.beneficiario.fluxo === 27) {
            // Situação = "Excedente", Etapa = "DEFIN"
            this.analiseDefinExcedente = true;
            return true;

        } else {
            return false
        }
    }

    protected exibirLiberar(): boolean {
        if (
            !this.verDiariaService.telaAprovador ||
            // !this.compararFluxo(this.beneficiario.fluxo_unicode, this.verDiariaService.fluxoViagem) ||
            !this.verDiariaService.etapasAprovador.includes(this.beneficiario.etapa_fluxo)
        ) {
            return false;

        } else if (this.beneficiario.fluxo === 48) {  
            //Situação = "Liberação de empenho", Etapa = "DG"
            this.liberacaoDG = true
            return true;

        } else {
            return false;
        }
    }

    compararFluxo(fluxoBenef: string, fluxoViagem: string): boolean {
        if (!fluxoBenef || !fluxoViagem) {
            return false;
        }
    
        const lastIndex = fluxoBenef.lastIndexOf(' - ');
        const etapaBenef = fluxoBenef.substring(0, lastIndex).trim();
        const situacaoBenef = fluxoBenef.substring(lastIndex + 3).trim();

        const firstIndex = fluxoViagem.indexOf(' - ');
        const situacaoViagem = fluxoViagem.substring(0, firstIndex).trim();
        const etapaViagem = fluxoViagem.substring(firstIndex + 3).trim();

        return (
            etapaBenef.trim() === etapaViagem.trim() && situacaoBenef.trim() === situacaoViagem.trim()
        );
    }

    protected refreshResumoBeneficiarios() {
        this.verDiariaService.refreshResumoBeneficiarios();
    }

    exibirBotaoChefeImediato(): boolean {
        return (
            this.isTelaChefeImediato &&
            this.beneficiario.fluxo === 20 // Aguardando ciência - Chefe imediato
        );
    }

    async irCienciaChefeImediato(deferir: boolean) {
        try {
            const response = await apiBenecificarioCienciaChefeImediato({
                beneficiario: this.beneficiario.id,
                cienciaChefe: deferir
            });
            this.refreshResumoBeneficiarios();
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || 'Não foi possível realizar a operação.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }

    get isTelaChefeImediato(): boolean {
        return this.verDiariaService.telaChefeImediato === true;
    }

    protected irEditarValor() {
        const dialogRef = this.dialog.open(EditarValorDeferidoDiariasComponent, {
            data: {
                beneficiarioID: this.beneficiario.id,
                extrato: this.extrato,
                onClose: () => {
                    this.carregarDadosBeneficiario(this.beneficiario.id);
                    this.refreshResumoBeneficiarios();
                },
            },
        });

        dialogRef.afterClosed().subscribe(() => {
            this.refreshResumoBeneficiarios();
        });
    }

    protected async irLiberar() {
        try {
            await apiBeneficiarioAnaliseDeplanCriar({
                beneficiario: this.beneficiario.id,
                empenho_liberado: true,
            }); 

            this.refreshResumoBeneficiarios();
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar a análise. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

    async exportarOs() {
        try {
            const result =
                await apiReportDiariasOsConsolidada({
                    id_beneficiario: this.beneficiario.id,
                });

            this.exibirMensagem('', result.message, 'sucess-snackbar');
        } catch (e: any) {
            console.error(e);
            this.exibirErro(e);
        }

    }

    protected exibirMensagem(
        titulo: string,
        texto: string,
        classe: string = 'custom-snackbar'
    ) {
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    protected exibirErro(e: any) {
        const detalheErro = e?.response?.data?.message || '';
        const texto = `Ocorreu um erro inesperado ao salvar. ${detalheErro}`;
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar'],
        });
    }

    podeEditarValor(): boolean {
        const etapasDefin = [11,12];
        const temEtapasDefin = etapasDefin.some((etapa) =>
            this.verDiariaService.etapasAprovador.includes(etapa)
        );
        return (
            this.beneficiario?.pode_editar_valor_deferido === true &&
            this.verDiariaService?.telaAprovador === true &&
            temEtapasDefin
        );
    }

    podeRecalcular(beneficiario:any): boolean {
        const etapasPermitidas = [13, 49];
        const etapaPermitida = etapasPermitidas.includes(beneficiario.fluxo)
    
        return (
            this.permicao_admin() &&
            this.verDiariaService?.telaAprovador &&
            etapaPermitida
        );
    }

    protected async recalcularViagem() {
        try {
            const response = await apiDiariasBeneficiarioRecalcular({id: this.beneficiario.id});

            this.exibirMensagem('Sucesso', 'Operação realizada com sucesso.');

        } catch (e: any) {
            console.error(e)
            const detalheErro = e?.response?.data?.message || 'Não foi possível realizar sa operação.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }


    booleano_string(value: boolean): string {
        return value ? 'SIM' : 'NÃO';
      }

    permicao_admin(): boolean {
        return this.perfil?.grupos.includes('ADMIN');
    }

    public async carregarPerfilAprovador(id: number) {
        try {
            this.perfil = (await apiDiariasPerfilAprovador({ id: id }));
        } catch (error) {
            console.error('Erro ao carregar os dados do perfil de aprovador do usuário logado :', error);
        }
    }
    

}

