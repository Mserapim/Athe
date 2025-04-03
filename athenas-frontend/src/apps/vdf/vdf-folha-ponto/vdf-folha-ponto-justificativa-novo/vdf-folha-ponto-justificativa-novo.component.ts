import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import {
    MAT_DIALOG_DATA,
    MatDialog,
    MatDialogRef,
} from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiFolhaPontoJustificativaCriar } from 'api/folha-ponto/api-folha-ponto-justificativa-criar.service';
import {
    apiFolhaPontoTiposJustificativas,
    ApiFolhaPontoTiposJustificativasItem,
} from 'api/folha-ponto/api-folha-ponto-tipos-justificativas.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';
import { addDay } from 'utils/add-day';
import { formatDate } from 'utils/format-date';

class VdfFolhaPontoJustificativaNovoComponentData {
    onClose?: Function;
    inicio?: Date;
    fim?: Date;
    ano?: number;
    mes?: number;
    servidor_id?: number;
}

@Component({
    selector: 'vdf-folha-ponto-justificativa-novo',
    templateUrl: 'vdf-folha-ponto-justificativa-novo.component.html',
    standalone: false
})
export class VdfFolhaPontoJustificativaNovoComponent extends MpmtFormularioComponent<VdfFolhaPontoJustificativaNovoComponentData> {
    modalButtons: ModalButton[] = [
        {
            label: 'Salvar',
            action: () => this.confirmarFormulario(),
            disabled: () => !this.formularioValido,
            color: 'white',
            backgroundColor: CoresPadraoEnum.verde
        }
    ];

    public startAt: Date;
    
    protected periodo = new FormGroup({
        data_inicio: new FormControl<string | Date>(undefined, []),
        data_fim: new FormControl<string | Date>(undefined, []),
    });

    protected formulario = new FormGroup({
        tipoJustificativa:
            new FormControl<ApiFolhaPontoTiposJustificativasItem>(undefined, [
                Validators.required,
            ]),
        data_inicio: new FormControl<Date>(undefined, [Validators.required]),
        dias: new FormControl<number>(1, [Validators.required]),
        data_fim: new FormControl<Date>(undefined, [Validators.required]),
        observacao: new FormControl<string>(undefined, []),
        anexo: new FormControl<{ valor: number }>(undefined, []),
        servidor_id: new FormControl<number>(undefined, []),
        tipo: new FormControl<'DIA' | 'HORA'>('DIA', []),
        origem: new FormControl<number>(4, []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: VdfFolhaPontoJustificativaNovoComponentData,
        protected dialogRef: MatDialogRef<VdfFolhaPontoJustificativaNovoComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
        public dialog: MatDialog
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');

        this.formulario.patchValue({
            servidor_id: this.data?.servidor_id || undefined,
        });

        if (this.data && this.data.inicio) {
            if (typeof (this.data.inicio as any).toDate === 'function') {
                this.startAt = (this.data.inicio as any).toDate();
            } else {
                this.startAt = this.data.inicio;
            }

        } else if (this.data && this.data.ano && this.data.mes) {
            this.startAt = new Date(this.data.ano, this.data.mes - 1, 1);
        } else {
            this.startAt = new Date();
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const {
            anexo,
            data_fim,
            data_inicio,
            observacao,
            servidor_id,
            origem,
            tipoJustificativa,
        } = this.formulario.value;

        try {
            const {} = await apiFolhaPontoJustificativaCriar({
                anexo_id: anexo?.valor,
                data_fim: formatDate(data_fim),
                data_inicio: formatDate(data_inicio),
                observacao,
                servidor_id,
                origem,
                tipo_justificativa:
                    tipoJustificativa?.value || tipoJustificativa?.id,
            });

            this.formulario.reset();
            this.fecharFormulario();
            if (this.data?.onClose) this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `${detalheErro}`;
            this.exibirMensagem('Atenção', texto);
        }
    }

    selecaoTipoJustificativas: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiFolhaPontoTiposJustificativas,
        obterValor: (payload) => {
            return payload;
        },
        obterTitulo: 'justificativa_display',
        obterFiltros: (payload) => {
            return {
                ...payload,
                servidor_id: this.data?.servidor_id || undefined,
                per_page: 10,
            };
        },
    };

    onChangeData($event) {
        const { dias, data_inicio } = this.formulario.value;

        if (!dias || dias <= 0 || dias > 1000) {
            this.formulario.patchValue({
                dias: 1,
            });
        }

        if (!data_inicio)
            this.formulario.patchValue({
                data_inicio: new Date(),
            });

        const { dias: diasAtualizado, data_inicio: dataInicioAtualizado } =
            this.formulario.value;

        return this.formulario.patchValue({
            data_fim: addDay(dataInicioAtualizado, diasAtualizado - 1),
        });
    }
}
