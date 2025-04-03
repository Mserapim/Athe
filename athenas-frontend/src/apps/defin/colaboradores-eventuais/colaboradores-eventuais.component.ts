import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ColaboradorEventualService } from './colaboradores-eventuais.service';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { ColaboradorEventualModalComponent } from './modal-colaborador-eventual/modal-colaborador-eventual.component';
import { DynamicDialogRef } from 'primeng/dynamicdialog';
import { PagamentoColaboradorEventualModalComponent } from './modal-pagamento-colaborador-eventual/modal-pagamento-colaborador-eventual.component';

import { ConfirmationService, MessageService } from 'primeng/api';
import { ConfirmDialog } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';
import { ButtonModule } from 'primeng/button';
import { apiDefinPagamentoColaboradorEventualApagar } from 'api/defin/pagamento-colaborador-eventual/api-defin-pagamento-apagar.service';
import { MatSnackBar } from '@angular/material/snack-bar';
@Component({
    selector: 'colaboradores-eventuais',
    templateUrl: 'colaboradores-eventuais.component.html',
    standalone: false,
    providers: [ConfirmationService, MessageService]

})
export class ColaboradorEventualComponent implements OnInit {

    constructor(
        public service: ColaboradorEventualService,
        public navegacaoAtualService: NavegacaoAtualService,
        public dialog: MatDialog,
        private confirmationService: ConfirmationService,
        protected snackBar: MatSnackBar,
        
        private messageService: MessageService
    ) { }

    ngOnInit() {
        this.service.irEditar = this.irEditar.bind(this);
    }

    ref: DynamicDialogRef | undefined;

    private irEditar(linha: any) {
        this.dialog.open(ColaboradorEventualModalComponent, {
            data: {
                colaborador_id: linha.id,
                onClose: () => { this.service.recarregar() },
            },
            width: '60%',
            height: '80%',
        });
    }

    private irNovo() {
        this.dialog.open(ColaboradorEventualModalComponent, {
            data: {
                onClose: () => { this.service.recarregar() },
            },
            width: '60%',
            height: '80%',
        });
    }


    private irNovoPagamento(linha: any) {

        this.dialog.open(PagamentoColaboradorEventualModalComponent, {
            data: {
                onClose: () => { this.service.recarregar() },
                colaborador_id: linha.id
            },
            width: '40%',
            height: '80%',
        });
    }

    private irEditarPagamento(linha: any) {

        this.dialog.open(PagamentoColaboradorEventualModalComponent, {
            data: {
                onClose: () => { this.service.recarregar() },
                id: linha.id,
                colaborador_id: linha.pessoa
            },
            width: '40%',
            height: '80%',
        });
    }

    irApagarPagamento(event: Event, item: any) {
        this.confirmationService.confirm({
            target: event.target as EventTarget,
            message: 'Tem certeza de que deseja apagar esse Pagamento?',
            header: 'Apagar Pagamento',
            closable: true,
            closeOnEscape: true,
            icon: 'pi pi-exclamation-triangle',
            rejectButtonProps: {
                label: 'Cancelar',
                severity: 'secondary',
                outlined: true,
            },
            acceptButtonProps: {
                label: 'Apagar',
                severity: 'danger',
            },
            accept: async () => {
                try{

                    var result = null;

                    result = await apiDefinPagamentoColaboradorEventualApagar({
                        id: item.id
                    });
                    
                    const resultado = result.data?.datail || "Pagamento Apagado"

                    this.exibirMensagem('', resultado, 'sucess-snackbar')

                    this.service.recarregar()


                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            },
            reject: () => {
                
            },
        });
    }

    protected exibirMensagem(
        titulo: string,
        texto: string,
        classe: string = 'custom-snackbar'
    ) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    protected exibirErro(e: any) {
        const detalheErro = e?.response?.data?.message || '';
        const texto = detalheErro || `Ocorreu um erro inesperado ao salvar`;
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar'],
        });
    }
}