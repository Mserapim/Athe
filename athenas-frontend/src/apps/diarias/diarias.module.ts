import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Route, RouterModule } from '@angular/router';
import { diariasRoute } from './diarias.route';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtListagemModule } from 'components/mpmt-listagem/mpmt-listagem.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { MpmtSelecaoModule } from 'components/mpmt-selecao/mpmt-selecao.module';
import { MpmtPicklistModule } from 'components/mpmt-picklist/mpmt-picklist.module';
import { MatTreeModule } from '@angular/material/tree';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { DiariasConfigCargosComponent } from './config/config-cargos/config-cargos.component';
import { DiariasConfigCargoNovoComponent } from './config/config-cargo-novo/config-cargo-novo.component';
import { DiariasConfigCargoEditarComponent } from './config/config-cargo-editar/config-cargo-editar.component';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { DiariasConfigCargosService } from './config/config-cargos/config-cargos.service';
import { DiariasConfigCargoApagarComponent } from './config/config-cargo-apagar/config-cargo-apagar.component';
import { DiariasConfigFluxosService } from './config/diarias-config-fluxos/diarias-config-fluxos.service';
import { DiariasConfigFluxosComponent } from './config/diarias-config-fluxos/diarias-config-fluxos.component';
import { DiariasConfigValoresService } from './config/config-valores/config-valores.service';
import { DiariasConfigValorNovoComponent } from './config/config-valor-novo/config-valor-novo.component';
import { DiariasConfigValoresComponent } from './config/config-valores/config-valores.component';
import { DiariasConfigValorEditarComponent } from './config/config-valor-editar/config-valor-editar.component';
import { DiariasConfigValorApagarComponent } from './config/config-valor-apagar/config-valor-apagar.component';
import { DiariasConfigFluxoNovoComponent } from './config/diarias-config-fluxo-novo/diarias-config-fluxo-novo.component';
import { DiariasConfigFluxoEditarComponent } from './config/diarias-config-fluxo-editar/diarias-config-fluxo-editar.component';
import { MpmtListagemReordenavelModule } from 'components/mpmt-listagem-reordenavel/mpmt-listagem-reordenavel.module';
import { DiariasConfigFluxoGerenciarDestinatariosComponent } from './config/diarias-config-fluxo-gerenciar-destinatarios/diarias-config-fluxo-gerenciar-destinatarios.component';
import { DiariasGruposAprovadoresService } from './config/grupo-aprovador/grupos-aprovadores/grupos-aprovadores.service';
import { DiariasGruposAprovadoresComponent } from './config/grupo-aprovador/grupos-aprovadores/grupos-aprovadores.component';
import { DiariasGrupoAprovadorNovoComponent } from './config/grupo-aprovador/grupo-aprovador-criar/grupo-aprovador-novo.component';
import { DiariasGrupoAprovadorEditarComponent } from './config/grupo-aprovador/grupo-aprovador-editar/grupo-aprovador-editar.component';
import { ViagensService } from './gestao/viagem/viagens.service';
import { ViagensComponent } from './gestao/viagem/viagens.component';
import { DiariasGrupoAprovadorEditarUsuariosComponent } from './config/grupo-aprovador/grupo-aprovador-editar-usuarios/grupo-aprovador-editar-usuarios.component';
import { MpmtAbasModule } from 'components/mpmt-abas/mpmt-abas.module';
import { VerDiariaComponent } from './gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.component';
import { VdfMinhasDiariasModule } from 'apps/vdf/minhas-diarias/minhas-diarias.module';
import { LimitesDiariasComponent } from './config/limite-diarias/limites-diarias.component';
import { LimitesDiariasService } from './config/limite-diarias/limites-diarias.service';
import { LimitesDiariasNovoComponent } from './config/limite-diarias/limite-diarias-criar/limite-diarias-novo.component';
import { LimiteDiariasEditarComponent } from './config/limite-diarias/limite-diarias-editar/limite-diarias-editar.component';
import {
    MpmtPicklistPaginadoApiModule
} from "../../components/mpmt-picklist-paginado-api/mpmt-picklist-paginado-api.module";
import { DiariasGestaoPagamentosComponent } from './gestao/pagamentos/diaria-pagamentos.component';
import { DiariasGestaoPagamentosService } from './gestao/pagamentos/diaria-pagamentos.service';
import { MpmtCabecalhoListagemModule } from 'components/mpmt-listagens/mpmt-cabecalho-listagem/mpmt-cabecalho-listagem.module';
import { MpmtListagemSelecaoModule } from 'components/mpmt-listagens/mpmt-listagem-selecao/mpmt-listagem-selecao.module';
import { PrestacaoContasComponent } from './gestao/prestacao-contas/modal-prestacao-contas/modal-prestacao-contas.component';
import { MpmtFileUpdateModule } from 'components/mpmt-file-update/mpmt-file-update.module';
import { PagamentoCnabCriarComponent } from './gestao/pagamentos/pagamentos-cnab/cnab-individual-criar.component';
import { PagamentoCnabEmMassaCriarComponent } from './gestao/pagamentos/pagamentos-cnab/cnab-multiplos-beneficiarios-criar.component';
import { CoreModule } from 'apps/core/core.module';
import { PrestacoesContasComponent } from './gestao/prestacao-contas/prestacoes-contas.component';
import { PrestacoesContasService } from './gestao/prestacao-contas/prestacoes-contas.service';
import { DiariaAnaliseCeafComponent } from './gestao/viagem/ver-diaria-aprovador/analise-diaria-ceaf/analise-diaria-ceaf.component';
import { DiariaAnaliseDeplanEmpenhoComponent } from './gestao/viagem/ver-diaria-aprovador/analises-diaria/analise-diaria-empenho-deplan/analise-diaria-deplan-empenho.component';
import { DiariaAnaliseDefinNotaComponent } from './gestao/viagem/ver-diaria-aprovador/analises-diaria/analise-defin-nota-liquidacao/analise-defin-nota-liquidacao.component';
import { DiariaAnaliseDefinOrdemBancariaComponent } from './gestao/viagem/ver-diaria-aprovador/analises-diaria/analise-defin-ordem-bancaria/analise-defin-ordem-bancaria.component';
import { MpmtTextoFormatadoModule } from 'components/mpmt-texto-formatado/mpmt-texto-formatado.module';
import { DiariaInformacaoAprovadorComponent } from './gestao/viagem/ver-diaria-aprovador/analises-diaria/informacao-e-aprovacao/informacao-e-aprovacao-diaria.component';
import { AprovarEditarNumeroDiariasComponent } from './gestao/viagem/ver-diaria-aprovador/analises-diaria/aprovar-e-alterar-numero-diarias/aprovar-e-alterar-numero-diarias.component';
import { AnaliseAssessoriaDgDiariasComponent } from './gestao/viagem/ver-diaria-aprovador/analises-diaria/analise-assessoria-dg/analise-assessoria-dg.component';
import { ManutencaoDadosBancariosComponent } from './gestao/pagamentos/manutencao-dados-bancarios/manutencao-dados-bancarios.component';
import { DaaCriarPassagemAereaComponent } from './gestao/viagem/ver-diaria-aprovador/daa-passagem-aerea/daa-passagem-aerea-criar.component';
import { DaaPassagemAereaComponent } from './gestao/viagem/ver-diaria-aprovador/daa-passagem-aerea/daa-passagem-aerea.component';
import { AnaliseDefinExcedenteComponent } from './gestao/viagem/ver-diaria-aprovador/analises-diaria/analise-defin-excedente/analise-defin-excedente.component';
import { DiariaAssessoriaAfatsamentoPGJComponent } from './gestao/viagem/ver-diaria-aprovador/analises-diaria/assessoria-pgj-afastamento/assessoria-pgj-afastamento.component';
import { CienciaCancelamentoComponent } from './gestao/viagem/ver-diaria-aprovador/ciencia-cancelamento-diarias/ciencia-cancelamento-diarias.component';
import { CondicionaisExplicacaoModalComponent } from './config/diarias-config-fluxo-novo/tutorial-condicionais/condicionais-explicacao.component';
import { DaaCriarMotoristaVeiculoComponent } from './gestao/viagem/ver-diaria-aprovador/daa-motorista-veiculo/daa-motorista-veiculo-criar.component';
import { DestinosService } from './gestao/viagem/ver-diaria-aprovador/daa-motorista-veiculo/diarias-destinos.service';
import { DaaMotoristaVeiculoComponent } from './gestao/viagem/ver-diaria-aprovador/daa-motorista-veiculo/daa-motorista-veiculo.component';
import { ListaBeneficiariosDiariasComponent } from './gestao/viagem/ver-beneficiarios-diaria/ver-beneficiarios-diaria.component';
import { MoverEtapaBeneficiarioComponent } from './gestao/viagem/ver-diaria-aprovador/analises-diaria/mover-etapa-especifica/mover-etapa-especifica.component';
import { MpmtSelecaoFormModule } from 'components/mpmt-selecao-form/mpmt-selecao-form.module';
import { DiariasConfigImportacaoComponent } from './config/importacao/importacao.component';
import { DiariasConfigImportacaoService } from './config/importacao/importacao.service';
import { MpmtFormTextoModule } from 'components/mpmt-form-texto/mpmt-form-texto.module';
import { MpmtFormMultiselecaoModule } from 'components/mpmt-form-multiselecao/mpmt-form-multiselecao.module';
import { MpmtFormMultiselecaoServidoresModule } from 'components/mpmt-form-multiselecao-servidores/mpmt-form-multiselecao-servidores.module';

const ROUTES: Route[] = [...diariasRoute];

const DECLARATIONS = [
    DiariasConfigImportacaoComponent,
    ManutencaoDadosBancariosComponent,
    DiariasConfigCargosComponent,
    DiariasConfigCargoNovoComponent,
    DiariasConfigCargoEditarComponent,
    DiariasConfigCargoApagarComponent,
    DiariasConfigValoresComponent,
    DiariasConfigValorNovoComponent,
    DiariasConfigValorEditarComponent,
    DiariasConfigValorApagarComponent,
    DiariasConfigFluxosComponent,
    DiariasConfigFluxoNovoComponent,
    DiariasConfigFluxoEditarComponent,
    DiariasConfigFluxoGerenciarDestinatariosComponent,
    DiariasGruposAprovadoresComponent,
    DiariasGrupoAprovadorNovoComponent,
    DiariasGrupoAprovadorEditarComponent,
    ViagensComponent,
    DiariasGrupoAprovadorEditarUsuariosComponent,
    DiariasGruposAprovadoresComponent,
    VerDiariaComponent,
    LimitesDiariasComponent,
    LimitesDiariasNovoComponent,
    LimiteDiariasEditarComponent,
    DiariasGestaoPagamentosComponent,
    PrestacaoContasComponent,
    PagamentoCnabCriarComponent,
    PagamentoCnabEmMassaCriarComponent,
    PrestacoesContasComponent,
    DiariaAnaliseCeafComponent,
    DiariaAnaliseDeplanEmpenhoComponent,
    DiariaAnaliseDefinNotaComponent,
    DiariaInformacaoAprovadorComponent,
    DiariaAnaliseDefinOrdemBancariaComponent,
    AprovarEditarNumeroDiariasComponent,
    AnaliseAssessoriaDgDiariasComponent,
    DaaCriarPassagemAereaComponent,
    DaaPassagemAereaComponent,
    AnaliseDefinExcedenteComponent,
    DiariaAssessoriaAfatsamentoPGJComponent,
    CienciaCancelamentoComponent,
    CondicionaisExplicacaoModalComponent,
    DaaCriarMotoristaVeiculoComponent,
    DaaMotoristaVeiculoComponent,
    ListaBeneficiariosDiariasComponent,
    MoverEtapaBeneficiarioComponent,
];

@NgModule({
    declarations: DECLARATIONS,
    providers: [
        DiariasConfigImportacaoService,
        DiariasConfigCargosService,
        DiariasConfigFluxosService,
        DiariasConfigValoresService,
        DiariasGruposAprovadoresService,
        ViagensService,
        LimitesDiariasService,
        PrestacoesContasService,
        DiariasGestaoPagamentosService,
        DestinosService,
    ],
    imports: [
        MpmtFormMultiselecaoServidoresModule,
        MpmtFormMultiselecaoModule,
        MpmtFormTextoModule,
        MpmtFileUpdateModule,
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MaterialModule,
        MpmtListagemModule,
        MpmtListagem2Module,
        MpmtListagemReordenavelModule,
        MpmtBotaoModule,
        MpmtSelecaoModule,
        MpmtPicklistModule,
        MpmtAbasModule,
        MatTreeModule,
        MatButtonModule,
        MatIconModule,
        RouterModule.forChild(ROUTES),
        VdfMinhasDiariasModule,
        MpmtPicklistPaginadoApiModule,
        MpmtListagemSelecaoModule,
        MpmtCabecalhoListagemModule,
        MpmtTextoFormatadoModule,
        MpmtSelecaoFormModule,
        CoreModule
    ],
    exports: [],
})
export class DiariasModule {}
