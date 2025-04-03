import { NgModule } from '@angular/core';
import { Route, RouterModule } from '@angular/router';
import { FolhaPontoRoute } from './folha-ponto.route';
import { CommonModule } from '@angular/common';
import { VdfFolhaPontoModule } from 'apps/vdf/vdf-folha-ponto/vdf-folha-ponto.module';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtSelecaoModule } from 'components/mpmt-selecao/mpmt-selecao.module';
import { MpmtArquivoModule } from 'components/mpmt-arquivo/mpmt-arquivo.module';
import { LayoutPadraoModalModule } from 'layout/mpmt-modal/layout-padrao-modal.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { CalendarModule } from 'primeng/calendar';
import { RadioButtonModule } from 'primeng/radiobutton';
import { MpPdfPreviewModule } from 'components/mp-pdf-preview/mp-pdf-preview.module';
import { VdfFolhaPontoService } from 'apps/vdf/vdf-folha-ponto/vdf-folha-ponto.service';

const route: Route[] = [...FolhaPontoRoute];

@NgModule({
    declarations: [],
    providers: [VdfFolhaPontoService],
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
        VdfFolhaPontoModule,
        MpPdfPreviewModule,
        RouterModule.forChild(route),
    ],
})
export class FolhaPontoModule {}
