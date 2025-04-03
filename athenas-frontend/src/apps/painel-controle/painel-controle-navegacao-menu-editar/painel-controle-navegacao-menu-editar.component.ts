import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoAcoes } from 'api/painel-controle/api-painel-controle-controle-acesso-acoes.service';
import { apiPainelControleControleAcessoGrupos } from 'api/painel-controle/api-painel-controle-controle-acesso-grupos.service';
import { apiPainelControleControleAcessoMenuConfigCriar } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-config-criar.service';
import { apiPainelControleControleAcessoMenuConfigEditar } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-config-editar.service';
import { apiPainelControleControleAcessoMenuConfigs } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-configs.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { MatSelectChange } from '@angular/material/select';
import { PainelControleNavegacaoMenuEditarMenuConfigsComponent } from '../painel-controle-navegacao-menu-editar-menuconfigs/painel-controle-navegacao-menu-editar-menuconfigs.component';

export class PainelControleNavegacaoMenuEditarComponentData {
    onClose?: Function;
    menuId?: number;
}

@Component({
    selector: 'painel-controle-navegacao-menu-editar',
    templateUrl: 'painel-controle-navegacao-menu-editar.component.html',
    standalone: false
})
export class PainelControleNavegacaoMenuEditarComponent extends MpmtFormularioComponent<PainelControleNavegacaoMenuEditarComponentData> {
    @ViewChild(PainelControleNavegacaoMenuEditarMenuConfigsComponent, {
        static: false,
    })
    painelControleNavegacaoMenuEditarMenuConfigsComponent: PainelControleNavegacaoMenuEditarMenuConfigsComponent;

    TODOS = 'Todos';
    acoes: string[] = [];

    ngOnInit() {
        this.carregarAcoes();
        this.formulario
            .get('usuario_grupo')
            .valueChanges.subscribe((grupoId) => {
                if (grupoId) {
                    this.carregarConfiguracoesGrupo(grupoId);
                }
            });
    }

    protected formulario = new FormGroup({
        acoes: new FormControl<string[]>([], [Validators.required]),
        usuario_grupo: new FormControl<number>(0, [Validators.required]),
    });

    menuConfigs = [];

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleNavegacaoMenuEditarComponentData,
        protected dialogRef: MatDialogRef<PainelControleNavegacaoMenuEditarComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async resetarFormulario() {
        super.resetarFormulario();
        console.log(this.data.menuId);
        try {
            const { results: menuConfigs } =
                await apiPainelControleControleAcessoMenuConfigs({
                    menu_id: this.data.menuId,
                });

            this.menuConfigs = menuConfigs;

            await this.formulario.reset();
        } catch (e) {
            console.log(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os valores do formulário'
            );
        }
    }

    protected async confirmarFormulario(event?: Event) {
        if (!this.formularioValido) return;

        this.formulario.controls.acoes.setValue(
            this.formulario.controls.acoes.value.filter(
                (acao) => acao != this.TODOS
            )
        );

        const { acoes, usuario_grupo } = this.formulario.value;
        try {
            if (this.menuConfigs) {
                const configuracoesExistentes = this.menuConfigs.find(
                    (config) => config.usuario_grupo
                );

                if (configuracoesExistentes) {
                    const response =
                        await apiPainelControleControleAcessoMenuConfigEditar({
                            id: configuracoesExistentes.id,
                            acoes: acoes,
                            menu: this.data.menuId,
                            usuario_grupo: +usuario_grupo,
                        });
                }
            } else {
                const response =
                    await apiPainelControleControleAcessoMenuConfigCriar({
                        acoes: acoes,
                        menu: this.data.menuId,
                        usuario_grupo: +usuario_grupo,
                    });
            }

            this.resetarFormulario();
            this.painelControleNavegacaoMenuEditarMenuConfigsComponent.ngOnChanges(
                null
            );
        } catch (e: any) {
            this.exibirErro(e);
        }
    }

    async carregarAcoes() {
        try {
            this.acoes = await apiPainelControleControleAcessoAcoes({});
        } catch (error) {
            console.error('Erro ao carregar as ações:', error);
            this.exibirMensagem('Erro', 'Não foi possível carregar as ações');
        }
    }

    async carregarConfiguracoesGrupo(grupoId: number) {
        try {
            const { results } =
                await apiPainelControleControleAcessoMenuConfigs({
                    menu_id: this.data.menuId,
                    usuario_grupo_id: grupoId,
                });
            this.menuConfigs = results;
            if (results && results.length > 0) {
                const acoesSelecionadas = results[0].acoes;
                this.formulario.get('acoes').setValue(acoesSelecionadas);
            } else {
                this.formulario.get('acoes').setValue([]);
            }
        } catch (e) {
            console.error('Erro ao carregar configurações do grupo:', e);
            this.exibirMensagem(
                'Erro',
                'Não foi possível carregar as configurações do grupo'
            );
            this.formulario.get('acoes').setValue([]);
        }
    }

    selecaoGrupos: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiPainelControleControleAcessoGrupos,
    };

    toggleAllSelection(): void {
        const currentValue = this.formulario.get('acoes')?.value;
        if (currentValue.includes(this.TODOS)) {
            this.formulario.get('acoes')?.setValue([]);
        } else {
            this.formulario.get('acoes')?.setValue([this.TODOS, ...this.acoes]);
        }
    }

    onSelectionChange(event: MatSelectChange): void {
        const currentValue = event.value;
        if (currentValue.includes(this.TODOS)) {
            if (currentValue.length === this.acoes.length + 1) {
                this.formulario
                    .get('acoes')
                    ?.setValue([this.TODOS, ...this.acoes]);
            } else {
                this.formulario.get('acoes')?.setValue([]);
            }
        } else {
            if (currentValue.length === this.acoes.length) {
                this.formulario
                    .get('acoes')
                    ?.setValue([this.TODOS, ...this.acoes]);
            } else {
                this.formulario
                    .get('acoes')
                    ?.setValue(
                        currentValue.filter(
                            (value: any) => value !== this.TODOS
                        )
                    );
            }
        }
    }

    mostrarTodosNaSelecao(): boolean {
        return this.acoes.length + 1 == this.formulario.value.acoes.length;
    }


    protected fecharFormulario() {
        this.data?.onClose()
        this.dialogRef.close();
    }

}
