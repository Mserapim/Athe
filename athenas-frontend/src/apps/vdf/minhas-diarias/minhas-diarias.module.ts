import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MinhasDiariasRoute } from './minhas-diarias.route';
import { MinhasDiariasComponent } from './minhas-diarias/minhas-diarias.component';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { MatIconModule } from '@angular/material/icon';
import { MinhasDiariasService } from './minhas-diarias/minhas-diarias.service';
import { MpmtFileUpdateModule } from 'components/mpmt-file-update/mpmt-file-update.module';
import { MpmtStepperModule } from 'components/mpmt-stepper/mpmt-stepper.module';
import { NovaDiariaComponent } from './nova-diaria/nova-diaria.component';
import { NovaDiariaStep1Component } from './nova-diaria/step1/viagem-step1.component';
import { NovaDiariaStep2Component } from './nova-diaria/step2/beneficiarios-step2.component';
import { NovaDiariaStep2Service } from './nova-diaria/step2/beneficiarios-step2.service';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MpmtSelecaoModule } from 'components/mpmt-selecao/mpmt-selecao.module';
import { DiariaStepperService } from './stepper/diaria-stepper.service';
import { DiariaStepperComponent } from './stepper/diaria-stepper.component';
import { NovoBeneficiarioComponent } from './novo-beneficiario/novo-beneficiario.component';
import { NovoDadosBancariosComponent } from './novo-dados-bancarios/novo-dados-bancarios.component';
import { NovaContaComponent } from './nova-conta/nova-conta.component';
import { NovoColaboradorEventualComponent } from './novo-colaborador-eventual/novo-colaborador-eventual.component';
import { NovaDiariaStep3Component } from './nova-diaria/step3/destinos-step3.component';
import { NovaDiariaStep3Service } from './nova-diaria/step3/destinos-step3.service';
import { NovoDestinoComponent } from './novo-destino/novo-destino.component';
import { MpmtAccordionModule } from 'components/mpmt-accordion/mpmt-accordion.module';
import { MpmtSelecaoFormModule } from 'components/mpmt-selecao-form/mpmt-selecao-form.module';
import { DetalhesDiariaComponent } from './detalhes/detalhes-diaria.component';
import { MpmtAbasModule } from 'components/mpmt-abas/mpmt-abas.module';
import { DetalhesViagemComponent } from './detalhes/resumo-diaria/detalhes-viagem.component';
import { FormatarNomePipe } from '@fuse/pipes/formatar-nome';
import { MpmtTimelineModule } from 'components/mpmt-timeline/mpmt-timeline.module';
import { HistoricoDiariaComponent } from './detalhes/historico-diaria/historico-diaria.component';
import { MpmtAcordeaoModule } from 'components/mpmt-acordeao/mpmt-acordeao.module';
import { ResumoBeneficiariosDiarias } from './detalhes/beneficiarios/resumo-beneficiarios.component';
import { DetalhesBeneficiariosComponent } from './detalhes/beneficiarios/beneficiario/detalhes-beneficiario.component';
import { SobreBeneficiarioComponent } from './detalhes/beneficiarios/beneficiario/sobre-beneficiario/sobre-beneficiario.component';
import { HistoricoBeneficiarioComponent } from './detalhes/beneficiarios/beneficiario/historico-beneficiario/historico-beneficiario.component';
import { TrechosDestinosBeneficiarioComponent } from './detalhes/beneficiarios/beneficiario/trechos-destinos/trechos-destinos.component';
import { ClonarDestinosComponent } from './clonar-destinos/clonar-destinos.component';
import { FuseConfirmationModule } from '@fuse/services/confirmation';
import { LimiteDiariasComponent } from './detalhes/beneficiarios/beneficiario/limites-uso-diarias/limites-uso-diarias.component';
import { MpmtListagemSelecaoModule } from 'components/mpmt-listagens/mpmt-listagem-selecao/mpmt-listagem-selecao.module';
import { FormularioEventoComponent } from './formulario-evento/formulario-evento.component';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { DiariaHistoricoDetalheComponent } from './detalhes/historico-diaria/historico-diaria-anexos-informacoes/historico-diaria-anexos-informacoes.component';
import { FormularioBeneficiarioComponent } from './formulario-beneficiario/formulario-beneficiario.component';
import { FormularioEventoService } from './formulario-beneficiario/formulario-beneficiario-eventos.service';
import { MpmtTextoFormatadoModule } from 'components/mpmt-texto-formatado/mpmt-texto-formatado.module';
import { DetalhesDiariaChefeImediatoComponent } from './ciencia-chefe-imediato/ciencia-chefe-imediato.component';
import { ClonarEventosParaComponent } from './clonar-eventos-para/clonar-eventos-para.component';
import { ClonarEventosDeComponent } from './clonar-eventos-de/clonar-eventos-de.component';
import { CancelarDiariaComponent } from './cancelar-diaria/cancelar-diaria.component';
import { EditarValorDeferidoDiariasComponent } from './detalhes/beneficiarios/beneficiario/sobre-beneficiario/valor-liquido-deferido-editar/valor-liquido-deferido-editar.component';
import { PrestacoesContasDiariasComponent } from './detalhes/beneficiarios/beneficiario/prestacao-contas/prestacao-contas-diarias.component';
const route: Route[] = [...MinhasDiariasRoute];

@NgModule({
    declarations: [
        CancelarDiariaComponent,
        ClonarEventosDeComponent,
        ClonarEventosParaComponent,
        FormularioBeneficiarioComponent,
        FormularioEventoComponent,
        ClonarDestinosComponent,
        MinhasDiariasComponent,
        NovaDiariaComponent,
        DiariaStepperComponent,
        NovaDiariaStep1Component,
        NovaDiariaStep2Component,
        NovoBeneficiarioComponent,
        NovoDadosBancariosComponent,
        NovaContaComponent,
        NovoColaboradorEventualComponent,
        NovaDiariaStep3Component,
        NovoDestinoComponent,
        DetalhesDiariaComponent,
        DetalhesViagemComponent,
        HistoricoDiariaComponent,
        HistoricoBeneficiarioComponent,
        ResumoBeneficiariosDiarias,
        DetalhesBeneficiariosComponent,
        FormatarNomePipe,
        SobreBeneficiarioComponent,
        TrechosDestinosBeneficiarioComponent,
        LimiteDiariasComponent,
        DiariaHistoricoDetalheComponent,
        DetalhesDiariaChefeImediatoComponent,
        EditarValorDeferidoDiariasComponent,
        PrestacoesContasDiariasComponent,
    ],
    exports: [MinhasDiariasComponent],
    providers: [
        MinhasDiariasService,
        DiariaStepperService,
        NovaDiariaStep2Service,
        NovaDiariaStep3Service,
        FormularioEventoService,
    ],
    imports: [

        MatDatepickerModule,
        MatNativeDateModule,
        MatCheckboxModule,
        MatButtonModule,
        MatSlideToggleModule,
        FuseConfirmationModule,
        MpmtSelecaoFormModule,
        MpmtAccordionModule,
        MatFormFieldModule,
        MatInputModule,
        MpmtSelecaoModule,
        MpmtFileUpdateModule,
        MpmtStepperModule,
        MatIconModule,
        MpmtListagem2Module,
        MpmtBotaoModule,
        MpmtAbasModule,
        MpmtTimelineModule,
        MpmtAcordeaoModule,
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        ReactiveFormsModule,
        MpmtListagemSelecaoModule,
        MpmtTextoFormatadoModule,
        RouterModule.forChild(route),
    ],
})
export class VdfMinhasDiariasModule {}
