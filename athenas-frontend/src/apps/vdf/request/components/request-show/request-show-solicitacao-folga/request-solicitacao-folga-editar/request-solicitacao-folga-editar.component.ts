import { Component, Inject } from '@angular/core';
import {
    MatDialogRef,
    MAT_DIALOG_DATA,
    MatDialog,
} from '@angular/material/dialog';
import { ApiVdfSolicitacaoFolgaEditarPayload, apiVdfSolicitacaoFolgaEditarService } from 'api/vdf/api-vdf-solicitacao-folga-editar.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { DateAdapter } from '@angular/material/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { addDay } from 'utils/add-day';

@Component({
    selector: 'request-solicitacao-folga-editar',
    templateUrl: 'request-solicitacao-folga-editar.html',
    standalone: false
})
export class RequestSolicitacaoFolgaEditarComponent {
    //observation: string = '';
    message: string;

    protected form = new FormGroup({
        dataInicio: new FormControl<Date | null>(null, [Validators.required]),
        dias: new FormControl<number>(1, [Validators.required]),
        dataFim: new FormControl<Date | null>(null, []),
        observacao: new FormControl<string>('', []),
        tipoItem: new FormControl<number>(null),
           
    });

    constructor(
        private dialogRef: MatDialogRef<RequestSolicitacaoFolgaEditarComponent>,
        @Inject(MAT_DIALOG_DATA) public data: any,
        protected currentUserService: CurrentUserService,
        protected dialog: MatDialog,
        protected dateAdapter: DateAdapter<Date>
    ) {
        this.dateAdapter.setLocale('pt-BR');
    }

    fechar(): void {
        this.dialogRef.close();
    }

    async ngOnInit() {
        this.carregarDados(this.data)
    }

    async goConfirm() {
        this.message = '';
        try {
            const response = await apiVdfSolicitacaoFolgaEditarService(this.postPayload());
            this.dialogRef.close();
        } catch (e) {
            this.message = e.response?.data?.message;
        }
    }

    public postPayload(){
        return <ApiVdfSolicitacaoFolgaEditarPayload>{
            data_inicio:this.form.value.dataInicio,
            data_fim:this.form.value.dataFim,
            tipo_folga:this.form.value.tipoItem,
            observation:this.form.value.observacao,
            id:this.data.id
        };
    }

    async carregarDados(dados):Promise<void> {
        this.form.patchValue({
            dataInicio: dados.data_inicio,
            dataFim: dados.data_fim,
            dias: dados.dias,
            tipoItem:dados.tipo_folga
        });
    }

    alterarDias($event) {
        this.form.value.dias = $event;
        if (!this.form.value.dataInicio || !this.form.value.dias) return;
            this.form.value.dataFim = addDay(
                this.form.value.dataInicio,
                this.form.value.dias - 1
            );
        
    }

    alterarDataInicio($event) {
        this.form.value.dataInicio = $event;
        if (!this.form.value.dataInicio) return;
        if (!this.form.value.dias) return;
        this.form.value.dataFim = addDay(
            this.form.value.dataInicio,
            this.form.value.dias - 1
        );
        
    }

    
}
