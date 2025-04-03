import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import {
    MAT_DIALOG_DATA,
    MatDialog,
    MatDialogRef,
} from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiFolhaPontoIgnorarBatida } from 'api/folha-ponto/api-folha-ponto-ignorar-batida.service';
import { ApiFolhaPontoMarcacoesItem } from 'api/folha-ponto/api-folha-ponto-marcacoes.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';

class VdfFolhaPontoMarcacaoEditarComponentData {
    onClose?: Function;
    marcacao?: ApiFolhaPontoMarcacoesItem;
}

@Component({
    selector: 'vdf-folha-ponto-marcacao-editar',
    templateUrl: 'vdf-folha-ponto-marcacao-editar.component.html',
    standalone: false
})
export class VdfFolhaPontoMarcacaoEditarComponent extends MpmtFormularioComponent<VdfFolhaPontoMarcacaoEditarComponentData> {
    protected formulario = new FormGroup({
        selecionados: new FormControl<number[]>([], []),
    });

    originalSelecionados: number[] = [];

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: VdfFolhaPontoMarcacaoEditarComponentData,
        protected dialogRef: MatDialogRef<VdfFolhaPontoMarcacaoEditarComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
        public dialog: MatDialog
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
        console.log(data.marcacao)
    }

    ngOnInit(): void {
        if (this.data.marcacao && this.data.marcacao.marcacoes) {
            const marcacoesInvalidas = this.data.marcacao.marcacoes
                .filter(marcacao => !marcacao.marcacao_valida)
                .map(marcacao => marcacao.id);
            this.originalSelecionados = [...marcacoesInvalidas];
            this.formulario.patchValue({
                selecionados: marcacoesInvalidas
            });
        }
    }

    modalButtons: ModalButton[] = [
        {
            label: 'Salvar',
            action: () => this.confirmarFormulario(),
            color: 'white',
            backgroundColor: CoresPadraoEnum.azul
        }
    ];

    get formularioEhValido() {
        const atual = this.formulario.value.selecionados as number[];
        return this.teveEstadoAlterado(this.originalSelecionados, atual);
    }

    protected async confirmarFormulario() {
        const original = this.originalSelecionados;
        const atual = this.formulario.value.selecionados as number[];

        const diffSet = new Set<number>();

        original.forEach(id => {
            if (!atual.includes(id)) {
                diffSet.add(id);
            }
        });
        atual.forEach(id => {
            if (!original.includes(id)) {
                diffSet.add(id);
            }
        });

        if (diffSet.size === 0) {
            return;
        }

        try {
            for await (const marcacao_id of Array.from(diffSet)) {
                await apiFolhaPontoIgnorarBatida({
                    marcacao_id,
                });
            }
            this.resetarFormulario();
            this.fecharFormulario();
            if (this.data?.onClose) this.data.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro =
                e?.response?.data?.resposta ||
                'Ocorreu um erro inesperado ao salvar o valor.';
            this.exibirMensagem('Atenção', detalheErro);
        }
    }

    private teveEstadoAlterado(original: number[], atual: number[]): boolean {
        if (original.length !== atual.length) {
            return true;
        }
        const sortedOriginal = [...original].sort();
        const sortedAtual = [...atual].sort();
        for (let i = 0; i < sortedOriginal.length; i++) {
            if (sortedOriginal[i] !== sortedAtual[i]) {
                return true;
            }
        }
        return false;
    }

    ehSelecionado(marcacao: any): boolean {
        return (this.formulario.value.selecionados || []).includes(marcacao.id);
    }

    mudarSelecionado($event: any, marcacao: any): void {
        const selecionados = this.formulario.value.selecionados as number[] || [];
        if ($event?.checked) {
            if (!selecionados.includes(marcacao.id)) {
                selecionados.push(marcacao.id);
            }
        } else {
            const novaLista = selecionados.filter((id: number) => id !== marcacao.id);
            this.formulario.patchValue({ selecionados: novaLista });
        }
    }
}
