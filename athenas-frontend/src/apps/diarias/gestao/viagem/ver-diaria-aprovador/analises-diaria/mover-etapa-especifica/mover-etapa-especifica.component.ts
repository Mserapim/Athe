import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiMoverFluxoBenecificarios } from 'api/diarias/analise-beneficiario/api-mover-fluxo-beneficiario.service';
import { apiDiariasBeneficiarios } from 'api/diarias/api-diaria-beneficiarios.service';
import { apiBenecificarioInformacaoEAprovacao } from 'api/diarias/aprovacoes-beneficiario/informacao-e-aprovacao.service';
import { apiDiariasConfigFluxos } from 'api/diarias/config/api-diarias-config-fluxos.service';
import { apiObservacaoHistoricoFluxoBeneficiario } from 'api/diarias/detalhe/api-historico-observacao-beneficiario.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoFormComponent, MpmtSelecaoFormComponentConfiguracao } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';
import { MpmtSelecaoComponent } from 'components/mpmt-selecao/mpmt-selecao.component';
import { BehaviorSubject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

class MoverEtapaBeneficiarioData {
    viagemId: number;
    onClose?: Function;
}

@Component({
    selector: 'mover-etapa-especifica',
    templateUrl: 'mover-etapa-especifica.component.html',
    standalone: false
})
export class MoverEtapaBeneficiarioComponent extends MpmtFormularioComponent<MoverEtapaBeneficiarioData> implements OnInit {
    @ViewChild('selecaoFluxoComponent') selecaoFluxoComponent: MpmtSelecaoFormComponent;

    protected formulario = new FormGroup({
        observacao: new FormControl<string>('', [Validators.required]),
        fluxo: new FormControl<any>(null, [Validators.required]),
    });

    beneficiarios: any[] = [];
    fluxos: any[] = [];
    fluxosFiltrados: any[] = [];
    displayedColumns: string[] = ['select', 'codigo_os', 'beneficiario', 'fluxo'];
    selectedBeneficiarios: number[] = [];
    private searchTerm = new BehaviorSubject<string>('');

    ngOnInit() {
        super.ngOnInit();
        this.carregarFluxos();
        this.setupFilter();
        this.carregarBeneficiarios();
    }

    async carregarFluxos() {
        try {
            const response = await apiDiariasConfigFluxos(null);
            this.fluxos = response.results;
            this.fluxosFiltrados = [...this.fluxos];
        } catch (error) {
            console.error('Erro ao carregar fluxos:', error);
        }
    }

    async carregarBeneficiarios() {
        try {
            const beneficiarios = await apiDiariasBeneficiarios({
                viagem_id: this.data.viagemId,
            });
            this.beneficiarios = beneficiarios.results.map((b: any) => ({ ...b, selected: false }));
        } catch (error) {
            console.error('Erro ao buscar dados', error);
        }
    }

    filtrarFluxos(term: string) {
        this.searchTerm.next(term);
    }

    setupFilter() {
        this.searchTerm.pipe(debounceTime(300)).subscribe((term) => {
            if (!term) {
                this.fluxosFiltrados = [...this.fluxos];
            } else {
                this.fluxosFiltrados = this.fluxos.filter((fluxo) =>
                    `${fluxo.ordem} - ${fluxo.situacao_display} - ${fluxo.etapa_display}`
                        .toLowerCase()
                        .includes(term.toLowerCase())
                );
            }
        });
    }

    toggleSelection(row: any) {
        if (row.selected) {
            this.selectedBeneficiarios.push(row.id);
        } else {
            this.selectedBeneficiarios = this.selectedBeneficiarios.filter((id) => id !== row.id);
        }
    }

    toggleAllSelection(selected: boolean) {
        this.beneficiarios.forEach((b) => (b.selected = selected));
        this.selectedBeneficiarios = selected
            ? this.beneficiarios.map((b) => b.id)
            : [];
    }

    async irConfirmar() {
        if (!this.formulario.valid) {
            this.snackBar.open('Preencha todos os campos obrigatórios!', '', { duration: 3000 });
            return;
        }

        if (this.selectedBeneficiarios.length === 0) {
            this.snackBar.open('Selecione pelo menos um beneficiário!', '', { duration: 3000 });
            return;
        }

        const { observacao, fluxo } = this.formulario.value;
        
        try {
            const response = await apiMoverFluxoBenecificarios({
                beneficiarios:this.selectedBeneficiarios,
                obs: observacao,
                fluxoEspecifico:fluxo.id,
            })


            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (error) {
            console.error('Erro ao salvar', error);
        }
    }

    displayFluxo(fluxo: any): string {
        return fluxo ? `${fluxo.ordem} - ${fluxo.situacao_display} - ${fluxo.etapa_display}` : '';
    }

    fecharFormulario() {
        this.dialogRef.close();
    }

    get habilitarSalvar(): boolean {
        return this.formulario.valid && this.selectedBeneficiarios.length > 0;
    }
}
