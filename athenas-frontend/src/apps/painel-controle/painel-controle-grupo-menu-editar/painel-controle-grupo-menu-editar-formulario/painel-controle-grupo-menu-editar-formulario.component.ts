import {
    Component,
    EventEmitter,
    Input,
    OnChanges,
    Output,
} from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoAcoes } from 'api/painel-controle/api-painel-controle-controle-acesso-acoes.service';
import { apiPainelControleControleAcessoGruposMenus } from 'api/painel-controle/api-painel-controle-controle-acesso-grupos-menus.service';
import { apiPainelControleControleAcessoMenuConfigCriar } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-config-criar.service';
import { apiPainelControleControleAcessoMenuConfigs } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-configs.service';
import { apiPainelControleControleAcessoModulos } from 'api/painel-controle/api-painel-controle-controle-acesso-modulos.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { BehaviorSubject, Observable, Subject, map } from 'rxjs';

export class PainelControleGrupoMenuEditarFormularioComponentData {}

@Component({
    selector: 'painel-controle-grupo-menu-editar-formulario',
    templateUrl: 'painel-controle-grupo-menu-editar-formulario.component.html',
    standalone: false
})
export class PainelControleGrupoMenuEditarFormularioComponent
    extends MpmtFormularioComponent<PainelControleGrupoMenuEditarFormularioComponentData>
    implements OnChanges
{
    @Input() usuarioGrupoId: string;
    @Input() menuId?: string;

    @Output() readonly onClose: EventEmitter<boolean> =
        new EventEmitter<boolean>();

    aberto: boolean = false;

    protected todasAcoesSubject: BehaviorSubject<string[]> =
        new BehaviorSubject<string[]>([]);

    protected formulario = new FormGroup({
        usuarioGrupoId: new FormControl<string>(null, [Validators.required]),
        moduloId: new FormControl<number>(null, [Validators.required]),
        menuId: new FormControl<string>(null, [Validators.required]),
        acoes: new FormControl<string[]>([], [Validators.required]),
    });

    constructor(
        protected dialogRef: MatDialogRef<{
            PainelControleGrupoMenuEditarFormularioComponentData;
        }>,
        protected snackBar: MatSnackBar
    ) {
        super({}, snackBar, dialogRef);
    }

    ngOnInit(): void {
        this.carregarTodasAcoes();
    }

    ngOnChanges(changes) {
        this.formulario.setValue({
            moduloId: null,
            acoes: [],
            usuarioGrupoId: this.usuarioGrupoId,
            menuId: null,
        });
    }

    public exibir() {
        this.aberto = true;
    }

    public ocultar() {
        this.aberto = false;
    }

    selecionarTodos() {
        const todosSelecionado =
            this.formulario.value?.acoes?.length ==
            this.todasAcoesSubject.value.length;

        if (!todosSelecionado) {
            const totalAcoes = this.todasAcoesSubject.value;
            this.formulario.patchValue({ acoes: totalAcoes });
        } else {
            this.formulario.patchValue({ acoes: [] });
        }
    }

    trocarSelecionado(acao: string) {
        const formularioAcoes = this.formulario.value?.acoes || [];
        if (!formularioAcoes.includes(acao)) {
            formularioAcoes.push(acao);
            this.formulario.patchValue({ acoes: formularioAcoes });
        } else {
            const acoesFiltrado = formularioAcoes.filter((x) => x != acao);
            this.formulario.patchValue({
                acoes: acoesFiltrado,
            });
        }
    }

    get situacaoIndeterminado(): boolean {
        return (
            this.formulario.value.acoes != null &&
            this.formulario.value?.acoes?.length > 0 &&
            this.formulario.value?.acoes?.length !=
                this.todasAcoesSubject?.value?.length
        );
    }

    get situacaoTodos(): boolean {
        return (
            this.formulario.value?.acoes?.length ==
            this.todasAcoesSubject?.value?.length
        );
    }

    public get todasAcoes$(): Observable<string[]> {
        return this.todasAcoesSubject.asObservable();
    }

    public acaoEstaSelecionada(acao) {
        return this.formulario.value?.acoes?.includes(acao);
    }

    async carregarTodasAcoes() {
        const acoes = await apiPainelControleControleAcessoAcoes({});
        this.todasAcoesSubject.next(acoes);
    }

    async carregarDadosParaEdicao() {
        const menuId = this.formulario.value.menuId;
        if (!menuId) return;
        const { results } = await apiPainelControleControleAcessoMenuConfigs({
            menu_id: menuId,
        });

        let acoes = [];
        if (results?.length > 0) acoes = results[0].acoes;

        this.formulario.patchValue({
            acoes,
        });
    }

    aoFechar(opened: boolean): void {
        this.aberto = opened;
        this.formulario.patchValue({
            moduloId: null,
            menuId: null,
            acoes: [],
        });
        if (!opened) this.onClose.emit();
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { acoes, menuId } = this.formulario.value;

        try {
            const {} = await apiPainelControleControleAcessoMenuConfigCriar({
                acoes: acoes,
                menu: +menuId,
                usuario_grupo: +this.usuarioGrupoId,
            });

            this.onClose.emit();
        } catch (e: any) {
            this.exibirErro(e);
        }
    }

    async aoSelecionarModulo() {
        this.formulario.patchValue({ menuId: null, acoes: [] });
    }

    selecaoModulos: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: payload => {
            return apiPainelControleControleAcessoModulos({situacao: "ATIVO"});
        },
    };

    selecaoMenus: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: async (payload) => this.obterOpcoesMenus(payload),
        obterFiltros: (payload) => this.obterFiltrosMenus(payload),
    };

    async obterOpcoesMenus(payload) {
        if (!payload?.modulo_id && !payload?.menu_id) return { results: [] };

        const items = await apiPainelControleControleAcessoGruposMenus({
            ...payload,
        });

        const items2 = {
            results: (items.results || [])?.flatMap((x) => {
                return x.menus.map((y) => {
                    return {
                        nome: `[${x.nome}] -  ${y.nome}`,
                        id: y.pk,
                    };
                });
            }),
        };

        return items2;
    }

    async obterFiltrosMenus(payload) {
        return {
            ...payload,
            modulo_id: this.formulario.value.moduloId
                ? this.formulario.value.moduloId
                : undefined,
            menu_id: this.formulario.value.menuId,
        };
    }

    async aoSelecionarMenu() {
        this.carregarDadosParaEdicao();
    }
}
