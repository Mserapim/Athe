import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoAcoes } from 'api/painel-controle/api-painel-controle-controle-acesso-acoes.service';
import {
    ApiPainelControleControleAcessoGruposMenusPayload,
    apiPainelControleControleAcessoGruposMenus,
} from 'api/painel-controle/api-painel-controle-controle-acesso-grupos-menus.service';
import { apiPainelControleControleAcessoGrupos } from 'api/painel-controle/api-painel-controle-controle-acesso-grupos.service';
import { apiPainelControleControleAcessoMenuConfigCriar } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-config-criar.service';
import { apiPainelControleControleAcessoMenuConfigs } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-configs.service';
import { apiPainelControleControleAcessoMenus } from 'api/painel-controle/api-painel-controle-controle-acesso-menus.service';
import { apiPainelControleControleAcessoModulos } from 'api/painel-controle/api-painel-controle-controle-acesso-modulos.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { MatSelectChange } from '@angular/material/select';
import { BehaviorSubject } from 'rxjs';
import { PainelControleGrupoMenuEditarListagemComponent } from './painel-controle-grupo-menu-editar-listagem/painel-controle-grupo-menu-editar-listagem.component';
import { PainelControleGrupoMenuEditarFormularioComponent } from './painel-controle-grupo-menu-editar-formulario/painel-controle-grupo-menu-editar-formulario.component';

export class PainelControleGrupoMenuEditarComponentData {
    onClose?: Function;
    usuarioGrupoId: number;
}

@Component({
    selector: 'painel-controle-grupo-menu-editar',
    templateUrl: 'painel-controle-grupo-menu-editar.component.html',
    styles: [``],
    standalone: false
})
export class PainelControleGrupoMenuEditarComponent extends MpmtFormularioComponent<PainelControleGrupoMenuEditarComponentData> {
    @ViewChild(PainelControleGrupoMenuEditarListagemComponent)
    listagemComponent: PainelControleGrupoMenuEditarListagemComponent;

    @ViewChild(PainelControleGrupoMenuEditarFormularioComponent)
    formularioComponent: PainelControleGrupoMenuEditarFormularioComponent;

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleGrupoMenuEditarComponentData,
        protected dialogRef: MatDialogRef<PainelControleGrupoMenuEditarComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {}

    irFormulario() {
        this.formularioComponent?.exibir();
    }

    aoFecharFormulario() {
        this.formularioComponent?.ocultar();
        this.listagemComponent?.recarregarListagem();
    }
}
