import { NgModule } from '@angular/core';
import { Route, RouterModule } from '@angular/router';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutModule } from 'layout/layout.module';
import { CommonModule } from '@angular/common';
import { VdfFolhaPontoComponent } from './vdf-folha-ponto.component';
import { VdfFolhaPontoService } from './vdf-folha-ponto.service';
import { VdfFolhaPontoRoute } from './vdf-folha-ponto.route';
import { MpmtSelecaoModule } from 'components/mpmt-selecao/mpmt-selecao.module';
import { RadioButtonModule } from 'primeng/radiobutton';
import { CalendarModule } from 'primeng/calendar';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { VdfFolhaPontoJustificativasComponent } from './vdf-folha-ponto-justificativas/vdf-folha-ponto-justificativas.component';
import { VdfFolhaPontoJustificativasService } from './vdf-folha-ponto-justificativas/vdf-folha-ponto-justificativas.service';
import { VdfFolhaPontoJustificativaNovoComponent } from './vdf-folha-ponto-justificativa-novo/vdf-folha-ponto-justificativa-novo.component';
import { MpmtArquivoModule } from 'components/mpmt-arquivo/mpmt-arquivo.module';
import { VdfFolhaPontoMarcacaoEditarComponent } from './vdf-folha-ponto-marcacao-editar/vdf-folha-ponto-marcacao-editar.component';
import { LayoutPadraoModalModule } from 'layout/mpmt-modal/layout-padrao-modal.module';
const route: Route[] = [...VdfFolhaPontoRoute];

@NgModule({
    declarations: [
        VdfFolhaPontoComponent,
        VdfFolhaPontoJustificativasComponent,
        VdfFolhaPontoJustificativaNovoComponent,
        VdfFolhaPontoMarcacaoEditarComponent,
    ],
    providers: [VdfFolhaPontoService, VdfFolhaPontoJustificativasService],
    imports: [
        CommonModule,
        LayoutModule,
        FormsModule,
        MaterialModule,
        ReactiveFormsModule,
        MpmtListagem2Module,
        MpmtSelecaoModule,
        RadioButtonModule,
        MaterialModule,
        CalendarModule,
        MpmtBotaoModule,
        MpmtArquivoModule,
        LayoutPadraoModalModule,
        RouterModule.forChild(route),
    ],
    exports: [
        VdfFolhaPontoComponent,
        VdfFolhaPontoJustificativasComponent,
        VdfFolhaPontoJustificativaNovoComponent,
        VdfFolhaPontoMarcacaoEditarComponent,
    ],
})
export class VdfFolhaPontoModule {}
