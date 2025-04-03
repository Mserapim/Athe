import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiAnotacoesPessoaisTiposDocumentos } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-tipos-documentos.service';
import { apiRhOrgaoGeral } from 'api/rh/api-rh-orgao-geral.service';
import { apiRhPublicacaoCriar } from 'api/rh/api-rh-publicacao-criar.service';
import { apiRhVeiculoPublicacao } from 'api/rh/api-rh-veiculo-publicacao.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';

class AnotacoesPessoaisNovoComponentData {
    onClose?: (publicacao?: any) => void;
}

@Component({
    selector: 'anotacoes-pessoais-publicacao-novo',
    templateUrl: 'anotacoes-pessoais-publicacao-novo.component.html',
    standalone: false
})
export class AnotacoesPessoaisPublicacaoNovoComponent extends MpmtFormularioComponent<AnotacoesPessoaisNovoComponentData> {
    tipos: any[] = [];
    origens: any[] = [];
    veiculos: any[] = [];

    protected formulario = new FormGroup({
        numero: new FormControl<string>('', []),
        tipo: new FormControl<any>(null),
        origem: new FormControl<any>(null, []),
        data_expedicao: new FormControl<string>(null, [Validators.required]),
        data_vigencia: new FormControl<string>(null, [Validators.required]),
        veiculo_publicacao: new FormControl<any>(null, []),
        numero_publicacao: new FormControl<string>(null, []),
        data_publicacao: new FormControl<Date>(null, []),
        vehicle_page: new FormControl<number>(null, []),
        interessado_nome: new FormControl<string>(null, []),
        arquivo: new FormControl<number>(null, []),
        interno: new FormControl<boolean>(false, []),
        observacao: new FormControl<string>(null, []),
        document: new FormControl<string>(null, []),
    });

    ngOnInit(): void {}

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: AnotacoesPessoaisNovoComponentData,
        protected dialogRef: MatDialogRef<AnotacoesPessoaisNovoComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>
    ) {
        super(data, snackBar, dialogRef);

        this.dateAdapter.setLocale('pt-BR');
    }

    protected async resetarFormulario() {
        super.resetarFormulario();
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const data = this.formulario.value;

        function extractDateString(date: any) {
            if (!date) return undefined;
            if (typeof date == 'string') return date;
            return date?.toDate()?.toISOString()?.substring(0, 10);
        }
        try {
            const veiculo_publicacao_value = data.veiculo_publicacao.value;
            const tipo_value = data.tipo.value;
            const origem_value = data.origem.value;
            const response: any = await apiRhPublicacaoCriar({
                ...(data as any),
                veiculo_publicacao: veiculo_publicacao_value,
                tipo: tipo_value,
                origem: origem_value,
                data_vigencia: extractDateString(data.data_vigencia),
                data_expedicao: extractDateString(data.data_expedicao),
                data_publicacao: extractDateString(data.data_publicacao),
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose(response.data);
        } catch (e: any) {
            console.log(e);
            const detalheErro =
                e?.response?.data?.message ||
                'Ocorreu um erro inesperado ao salvar';
            const texto = `${detalheErro}`;
            this.exibirMensagem('Atenção', texto);
        }
    }

    selecaoOrgaoGeral: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiRhOrgaoGeral,
        obterValor: 'id',
        obterTitulo: 'nome',
    };

    selecaoVeiculoPublicacao: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiRhVeiculoPublicacao,
        obterValor: 'value',
        obterTitulo: 'label',
    };

    selecaoAnotacaoPessoalTiposDocumentos: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiAnotacoesPessoaisTiposDocumentos,
        obterValor: 'value',
        obterTitulo: 'label',
    };

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];
}
