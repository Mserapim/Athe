import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { PainelControleModulosComponent } from './painel-controle-modulos/painel-controle-modulos.component';
import { Route, RouterModule } from '@angular/router';
import { painelControleRoute } from './painel-controle.route';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtListagemModule } from 'components/mpmt-listagem/mpmt-listagem.module';
import { PainelControleModuloNovoComponent } from './painel-controle-modulo-novo/painel-controle-modulo-novo.component';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { PainelControleModuloEditarComponent } from './painel-controle-modulo-editar/painel-controle-modulo-editar.component';
import { PainelControleNavegacaoComponent } from './painel-controle-navegacao/painel-controle-navegacao.component';
import { MpmtSelecaoModule } from 'components/mpmt-selecao/mpmt-selecao.module';
import { PainelControleNavegacaoGrupoMenuCriarComponent } from './painel-controle-navegacao-grupo-menu-criar/painel-controle-navegacao-grupo-menu-criar.component';
import { PainelControleNavegacaoMenuCriarComponent } from './painel-controle-navegacao-menu-criar/painel-controle-navegacao-menu-criar.component';
import { PainelControleNavegacaoMenuEditarComponent } from './painel-controle-navegacao-menu-editar/painel-controle-navegacao-menu-editar.component';
import { PainelControleNavegacaoMenuEditarMenuConfigsComponent } from './painel-controle-navegacao-menu-editar-menuconfigs/painel-controle-navegacao-menu-editar-menuconfigs.component';
import { PainelControleGrupoMenuEditarMenuConfigsComponent } from './painel-controle-grupo-menu-editar-menuconfigs/painel-controle-grupo-menu-editar-menuconfigs.component';
import { PainelControleGrupoMenuEditarComponent } from './painel-controle-grupo-menu-editar/painel-controle-grupo-menu-editar.component';
import { PainelControleNavegacaoMenuListarUsuariosComponent } from './painel-controle-navegacao-menu-listar-usuarios/painel-controle-navegacao-menu-listar-usuarios.component';
import { PainelControleGruposComponent } from './painel-controle-grupos/painel-controle-grupos.component';
import { PainelControleGrupoNovoComponent } from './painel-controle-grupo-novo/painel-controle-grupo-novo.component';
import { PainelControleGrupoEditarComponent } from './painel-controle-grupo-editar/painel-controle-grupo-editar.component';
import { PainelControleUsuariosComponent } from './painel-controle-usuarios/painel-controle-usuarios.component';
import { PainelControleUsuarioEditarComponent } from './painel-controle-usuario-editar/painel-controle-usuario-editar.component';
import { PainelControleNavegacaoMenuEditarConfiguracaoComponent } from './painel-controle-navegacao-menu-editar-configuracoes/painel-controle-navegacao-menu-editar.component';
import { PainelControleUsuarioAtualizarGruposComponent } from './painel-controle-usuario-atualizar-grupos/painel-controle-usuario-atualizar-grupos.component';
import { MpmtPicklistModule } from 'components/mpmt-picklist/mpmt-picklist.module';
import { PainelControleUsuarioEstruturaMenusComponent } from './painel-controle-usuario-atualizar-estrutura-menus/painel-controle-usuario-estrutura-menus.component';
import { MatTreeModule } from '@angular/material/tree';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { PainelControleNavegacaoGrupoMenuEditarComponent } from './painel-controle-navegacao-grupo-menu-editar/painel-controle-navegacao-grupo-menu-editar.component';
import { PainelControleNavegacaoMenuEditarUsuariosComponent } from './painel-controle-navegacao-menu-editar-usuarios/painel-controle-navegacao-menu-editar-usuarios.component';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { PainelControleModulosService } from './painel-controle-modulos/painel-controle-modulos.service';
import { PainelControleGrupoAtualizarUsuariosComponent } from './painel-controle-grupo-atualizar-usuarios/painel-controle-grupo-atualizar-usuarios.component';
import { PainelControleUsuarioAtualizarGruposService } from './painel-controle-usuario-atualizar-grupos/painel-controle-usuario-atualizar-grupos.service';
import { PainelControleGrupoAtualizarUsuariosService } from './painel-controle-grupo-atualizar-usuarios/painel-controle-grupo-atualizar-usuarios.service';
import { MpmtSelecaoIconesModule } from '../../components/mpmt-selecao-icones/mpmt-selecao-icones.module';
import { MpmtPaginaTituloModule } from 'components/mpmt-pagina-titulo/mpmt-pagina-titulo.module';
import { PainelControleGruposService } from './painel-controle-grupos/painel-controle-grupos.service';
import { PainelControleUsuariosService } from './painel-controle-usuarios/painel-controle-usuarios.service';
import { FuseDrawerModule } from '@fuse/components/drawer';
import { PainelControleGrupoMenuEditarListagemService } from './painel-controle-grupo-menu-editar/painel-controle-grupo-menu-editar-listagem/painel-controle-grupo-menu-editar-listagem.service';
import { PainelControleGrupoMenuEditarListagemComponent } from './painel-controle-grupo-menu-editar/painel-controle-grupo-menu-editar-listagem/painel-controle-grupo-menu-editar-listagem.component';
import { PainelControleGrupoMenuEditarFormularioComponent } from './painel-controle-grupo-menu-editar/painel-controle-grupo-menu-editar-formulario/painel-controle-grupo-menu-editar-formulario.component';
import {
    MpmtPicklistPaginadoApiModule
} from "../../components/mpmt-picklist-paginado-api/mpmt-picklist-paginado-api.module";
import { PainelControleServicosComponent } from './painel-controle-servicos/painel-controle-servicos.component';
import { PainelControleServicosService } from './painel-controle-servicos/painel-controle-servicos.service';
import { PainelControleServicoNovoComponent } from './painel-controle-servico-novo/painel-controle-servico-novo.component';
import { PainelControleServicoEditarComponent } from './painel-controle-servico-editar/painel-controle-servico-editar.component';
import { MpmtListagemSelecaoModule } from 'components/mpmt-listagens/mpmt-listagem-selecao/mpmt-listagem-selecao.module';
import { ModalClasscodesComponent } from './classcodes/modal-classcodes/modal-classcodes.component';
import { ClasscodesService } from './classcodes/modal-classcodes/modal-classcodes.component.service';
import { PainelControleClasscodeNovoComponent } from './classcodes/painel-controle-classcode-novo/painel-controle-classcode-novo.component';
import { PainelControleClasscodeEditarComponent } from './classcodes/painel-controle-classcode-editar/painel-controle-classcode-editar.component';
import { PainelControleClasscodeApagarComponent } from './classcodes/painel-controle-classcode-apagar/painel-controle-classcode-apagar.component';
import { PainelControleServicoApagarComponent } from './painel-controle-servico-apagar/painel-controle-servico-apagar.component';
import { MpmtSelecaoFormModule } from 'components/mpmt-selecao-form/mpmt-selecao-form.module';
import {LayoutPadraoModalModule} from "../../layout/mpmt-modal/layout-padrao-modal.module";
import { PainelControleConfigPontoComponent } from './painel-controle-configuracao-configuracao-de-ponto/painel-controle-configuracao-configuracao-de-ponto.component';
import { PainelControleConfigPontoService } from './painel-controle-configuracao-configuracao-de-ponto/painel-controle-configuracao-configuracao-de-ponto.service'
import { PainelControleConfigPontoCRUDComponent } from './painel-controle-configuracao-configuracao-de-ponto-crud/painel-controle-configuracao-configuracao-de-ponto-crud.component';
import { PainelControleHistoricoServicosComponent } from './painel-controle-historico-servicos/painel-controle-historico-servicos.component';
import { PainelControleHistoricoServicosService } from './painel-controle-historico-servicos/painel-controle-historico-servicos.service';
import { ModalMensagensComponent } from './modal-mensagens/modal-mensagens.component';
import { MensagensService } from './modal-mensagens/modal-mensagens.component.service';
import { AuditoriaLogsComponent } from './painel-controle-auditoria-logs/painel-controle-auditoria-logs.component';
import { AuditoriaLogsService } from './painel-controle-auditoria-logs/painel-controle-auditoria-logs.service';
import { MpmtPaginaListagemModule } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.module';
import { MpmtFormMultiselecaoModule } from 'components/mpmt-form-multiselecao/mpmt-form-multiselecao.module';
import { MpmtFormPeriodoModule } from 'components/mpmt-form-periodo/mpmt-form-periodo.module';
import { MpmtFormTextoModule } from 'components/mpmt-form-texto/mpmt-form-texto.module';
import { AuditoriaLogsModalComponent } from './painel-controle-auditoria-logs/modal-auditoria-logs/modal-auditoria-logs.component';
import { MpmtVerMaisModule } from 'components/mpmt-ver-mais/mpmt-ver-mais.module';

const ROUTES: Route[] = [...painelControleRoute];

const DECLARATIONS = [
    PainelControleModulosComponent,
    PainelControleModuloNovoComponent,
    PainelControleModuloEditarComponent,
    PainelControleNavegacaoComponent,
    PainelControleNavegacaoGrupoMenuCriarComponent,
    PainelControleNavegacaoGrupoMenuEditarComponent,
    PainelControleNavegacaoMenuCriarComponent,
    PainelControleNavegacaoMenuEditarComponent,
    PainelControleNavegacaoMenuEditarMenuConfigsComponent,
    PainelControleNavegacaoMenuEditarUsuariosComponent,
    PainelControleGruposComponent,
    PainelControleGrupoNovoComponent,
    PainelControleGrupoEditarComponent,
    PainelControleUsuariosComponent,
    PainelControleUsuarioEditarComponent,
    PainelControleGrupoMenuEditarComponent,
    PainelControleGrupoMenuEditarListagemComponent,
    PainelControleGrupoMenuEditarFormularioComponent,
    PainelControleGrupoMenuEditarMenuConfigsComponent,
    PainelControleUsuarioAtualizarGruposComponent,
    PainelControleUsuarioEstruturaMenusComponent,
    PainelControleNavegacaoMenuEditarConfiguracaoComponent,
    PainelControleNavegacaoMenuListarUsuariosComponent,
    PainelControleGrupoAtualizarUsuariosComponent,
    PainelControleServicosComponent,
    PainelControleServicoNovoComponent,
    PainelControleServicoEditarComponent,
    PainelControleServicoApagarComponent,
    ModalClasscodesComponent,
    PainelControleClasscodeNovoComponent,
    PainelControleClasscodeEditarComponent,
    PainelControleClasscodeApagarComponent,
    PainelControleConfigPontoComponent,
    PainelControleConfigPontoCRUDComponent,
    PainelControleHistoricoServicosComponent,
    ModalMensagensComponent,
    AuditoriaLogsComponent,
    AuditoriaLogsModalComponent,
];

@NgModule({
    declarations: DECLARATIONS,
    providers: [
        PainelControleModulosService,
        PainelControleUsuarioAtualizarGruposService,
        PainelControleGrupoAtualizarUsuariosService,
        PainelControleGruposService,
        PainelControleUsuariosService,
        PainelControleGrupoMenuEditarListagemService,
        PainelControleServicosService,
        ClasscodesService,
        PainelControleConfigPontoService,
        PainelControleHistoricoServicosService,
        MensagensService,
        AuditoriaLogsService,
    ],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MaterialModule,
        MpmtListagemModule,
        MpmtListagem2Module,
        MpmtBotaoModule,
        MpmtSelecaoModule,
        MpmtPicklistModule,
        MatTreeModule,
        MatButtonModule,
        MatIconModule,
        FuseDrawerModule,
        MpmtPaginaTituloModule,
        RouterModule.forChild(ROUTES),
        MpmtSelecaoIconesModule,
        MpmtPicklistPaginadoApiModule,
        MpmtListagemSelecaoModule,
        MpmtSelecaoFormModule,
        LayoutPadraoModalModule,
        MpmtPaginaListagemModule,
        MpmtFormMultiselecaoModule,
        MpmtFormPeriodoModule,
        MpmtFormTextoModule,
        MpmtVerMaisModule,
    ],
    exports: [],
})
export class PainelControleModule {}
