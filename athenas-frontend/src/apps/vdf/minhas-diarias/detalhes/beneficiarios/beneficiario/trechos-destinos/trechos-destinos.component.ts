import { Component, OnInit } from "@angular/core";
import { MatSnackBar } from "@angular/material/snack-bar";
import { BeneficiarioService } from "../beneficiario.service";
import { apiDiariasDestinos } from "api/diarias/api-diarias-destinos.service";
import { apiDiariasBeneficiario } from "api/diarias/api-diarias-beneficiario.service";
import { DaaCriarPassagemAereaComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/daa-passagem-aerea/daa-passagem-aerea-criar.component";
import { MatDialog } from "@angular/material/dialog";
import { VerDiariaService } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.service";
import { DaaPassagemAereaComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/daa-passagem-aerea/daa-passagem-aerea.component";
import { DaaCriarMotoristaVeiculoComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/daa-motorista-veiculo/daa-motorista-veiculo-criar.component";
import { DaaMotoristaVeiculoComponent } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/daa-motorista-veiculo/daa-motorista-veiculo.component";

@Component({
    selector: 'trechos-destinos-beneficiario',
    templateUrl: './trechos-destinos.component.html',
    styleUrls: ['./trechos-destinos.component.scss'],
    standalone: false
})
export class TrechosDestinosBeneficiarioComponent implements OnInit {
    protected snackBar: MatSnackBar;
    destinos: any = [];
    beneficiario: any = {};

    constructor(
        private beneficiarioService: BeneficiarioService,
        private verDiariaService: VerDiariaService,
        public dialog: MatDialog,
    ) {}

    ngOnInit() {
        this.beneficiarioService.beneficiarioIdAtual.subscribe(beneficiarioId => {
            if (beneficiarioId != null) {
              this.carregarDestinosBeneficiario(beneficiarioId);
              this.carregarDadosBeneficiario(beneficiarioId);
            }
        });
    }

    async carregarDestinosBeneficiario(beneficiarioId: number) {
        try {
            const destinos = await apiDiariasDestinos({ beneficiario: beneficiarioId });
            this.destinos = destinos.results;
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }

    async carregarDadosBeneficiario(beneficiarioId: number) {
        try {
            const beneficiario = await apiDiariasBeneficiario({ id: beneficiarioId });
            this.beneficiario = beneficiario;
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }

    protected exibirMensagem(titulo: string, texto: string) {
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar']
        });
    }

    formatarBooleano = (valor: boolean) => valor ? 'Sim' : 'Não';

    protected exibirBotaoPassagemAerea(destino: any): boolean {
        const etapaDaaPassagem = 2
        if (
            !this.verDiariaService.telaAprovador ||
            (this.beneficiario.etapa_fluxo != etapaDaaPassagem) ||
            destino.analise_daa ||
            !this.verDiariaService.etapasAprovador.includes(this.beneficiario.etapa_fluxo)
        ) {
            return false;
        } else if (this.beneficiario.fluxo == 8 && destino.forma_deslocamento == 1) {
            return true;
        }
        return false;
    }

    protected exibirBotaoVeiculoMotorista(destino: any): { mostrar: boolean, texto: string } {
        const etapaDaaVeiculo = 21
        if (
            !this.verDiariaService.telaAprovador ||
            (this.beneficiario.etapa_fluxo != etapaDaaVeiculo) ||
            destino.analise_daa ||
            !this.verDiariaService.etapasAprovador.includes(this.beneficiario.etapa_fluxo)
        ) {
            return { mostrar: false, texto: '' };
            
        } else if (this.beneficiario.fluxo == 46 && destino.forma_deslocamento == 2) {
            if (destino.com_motorista) {
                if (destino.veiculo_daa) {
                    return { mostrar: true, texto: 'Adicionar veículo e motorista' };
                } else {
                    return { mostrar: true, texto: 'Adicionar motorista' };
                }
            } else if (destino.veiculo_daa) {
                return { mostrar: true, texto: 'Adicionar veículo' };
            }
        }
        return { mostrar: false, texto: '' };
    }

    compararFluxo(fluxoBenef: string, fluxoViagem: string): boolean {
        const [etapaBenef, subEtapaBenef] = fluxoBenef.split(' - ');
        const [etapaViagem, subEtapaViagem] = fluxoViagem.split(' - ');
        return (
            etapaBenef === etapaViagem && subEtapaBenef === subEtapaViagem
        );
    }

    protected adicionarPassagemAerea(destino: any) {
        this.dialog.open(DaaCriarPassagemAereaComponent, {
            data: { 
                destinoId: destino.id,
                onClose: () => {
                    this.carregarDestinosBeneficiario(this.beneficiario.id);
                },
            },
        });
    }

    protected adicionarVeiculoMotorista(destino: any) {
        this.dialog.open(DaaCriarMotoristaVeiculoComponent, {
            data: { 
                destinoId: destino.id,
                viagemID: this.verDiariaService.viagemId,
                comMotorista: destino.com_motorista,
                veiculoDaa: destino.veiculo_daa,
                onClose: () => {
                    this.carregarDestinosBeneficiario(this.beneficiario.id);
                },
            },
        });
    }

    protected exibirBotaoVerPassagemAerea(destino: any): boolean {
        return (destino.analise_daa === true && destino.forma_deslocamento == 1);
    }

    protected exibirBotaoVerMotoristaVeiculo(destino: any): boolean {
        return (destino.analise_daa === true && destino.forma_deslocamento == 2);
    }

    protected verPassagemAerea(destino: any) {
        this.dialog.open(DaaPassagemAereaComponent, {
            data: { 
                destinoId: destino.id,
                onClose: () => {
                    this.carregarDestinosBeneficiario(this.beneficiario.id);
                },
            },
        });
    }

    protected verMotoristaVeiculo(destino: any) {
        this.dialog.open(DaaMotoristaVeiculoComponent, {
            data: { 
                destinoId: destino.id,
                onClose: () => {
                    this.carregarDestinosBeneficiario(this.beneficiario.id);
                },
            },
        });
    }
}