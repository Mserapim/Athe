import { Component, Input, OnInit } from '@angular/core';
import { useGedDownload } from 'api/@base/use-ged-download';
import { printDate } from 'utils/print-date'
import { apiVdfDetalhesSolicitacaoFolga,ApiDetalheSolicitacaoFolgaPayload } from 'api/vdf/api-vdf-solicitacao-folga.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { stringToDate } from 'utils/string-to-date';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { ApiRhPvfRequestsIdResponse } from 'api/rh/api-rh-pvf-requests-id.service';
import { RequestStatusEnum } from 'enums/request-status.enum';
import { DateAdapter } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { RequestSolicitacaoFolgaEditarComponent } from './request-solicitacao-folga-editar/request-solicitacao-folga-editar.component';

@Component({
    selector: 'request-show-solicitacao-folga',
    templateUrl: './request-show-solicitacao-folga.component.html',
    standalone: false
})
export class RequestShowSolicitacaoFolgaComponent implements OnInit {
    @Input() requestId!: number;
    @Input() request: ApiRhPvfRequestsIdResponse = {};


    public data: any = {};
    public message:string

    protected form = new FormGroup({
        dataInicio: new FormControl<Date | null>(null, [Validators.required]),
        dias: new FormControl<number>(1, [Validators.required]),
        dataFim: new FormControl<Date | null>(null, []),
        observacao: new FormControl<string>('', []),
        tipoItem: new FormControl<number>(null),
           
    });

    constructor(
        protected currentUserService: CurrentUserService,
        protected dialog: MatDialog,
        protected dateAdapter: DateAdapter<Date>

    ) {
        this.dateAdapter.setLocale('pt-BR');
    }

    ngOnInit() {
        this.form.disable()
    }

    printDate = printDate;

    async ngOnChanges() {
        this.load()
    }

    async load(){
        try {
            const response = await apiVdfDetalhesSolicitacaoFolga(this.payload());
            this.carregarDados(response)
            this.data = response;
        } catch (e) {
            console.log(e);
        }
    }

    goConfirm() {
        const dialogRef = this.dialog.open(RequestSolicitacaoFolgaEditarComponent, {
            width: '700px',
            data: { 
                data_inicio:this.form.value.dataInicio,
                data_fim:this.form.value.dataFim,
                tipo_folga:this.form.value.tipoItem,
                dias: this.form.value.dias,
                id:this.requestId
             },
        });
        dialogRef.afterClosed().subscribe((result) => {
            this.load().then()
        });
    }

    async carregarDados(dados):Promise<void> {
        this.form.patchValue({
            dataInicio: stringToDate(dados.data_inicio),
            dataFim: stringToDate(dados.data_fim),
            dias: dados.dias,
            tipoItem:dados.tipo_folga
        });
    }

    public payload() {
        return <ApiDetalheSolicitacaoFolgaPayload>{
            id:this.requestId
        };
    }

    isAprovadorDgp():boolean{
        let grupos = this.currentUserService.currentUser.group_details
        let valor = grupos.some(grupo => 
            grupo.name == 'mpmt-perfil-vdf-aprovador-servidores' ||  
            grupo.name == 'mpmt-perfil-vdf-aprovador-membros' 
        )
        if (!valor)
            return false
        return true
    }

    isSolitacaoAndamento():boolean{
        if (this.request.status == RequestStatusEnum.EFETIVADO ||
            this.request.status == RequestStatusEnum.CANCELADO_DGP ||
            this.request.status == RequestStatusEnum.INDEFERIDO
        ){
           return false
        }
        return true
    }

    async download(file_id) {
        useGedDownload(file_id);
    }

   
}
