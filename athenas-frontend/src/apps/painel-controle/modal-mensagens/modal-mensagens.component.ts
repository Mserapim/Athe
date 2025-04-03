import { Component, Inject } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MensagensService } from './modal-mensagens.component.service';
import moment from 'moment';

class ModalMensagensComponentData {
    selecionada?: number;
    onClose?: Function;
}


@Component({
    selector: 'modal-mensagens',
    templateUrl: './modal-mensagens.component.html',
    styleUrls: ['./modal-mensagens.component.scss'],
    standalone: false
})
export class ModalMensagensComponent extends MpmtFormularioComponent<ModalMensagensComponentData> {

    protected titulo: string = "Mensagens";

    loading = true

    protected formulario = new FormGroup({

    });
    
    protected get formularioValido() {
        return this.formulario.valid;
    }

    dadosUnicos: any = {};

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: ModalMensagensComponentData,
        protected service: MensagensService,
        protected dialogRef: MatDialogRef<ModalMensagensComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,

    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {
        this.loading = true
        this.service.selecionada = this.data?.selecionada;
        this.configurarColunas();
        this.service.recarregarListagem();
        this.service.listagem$.subscribe(lista => {
            if (lista.length > 0) {
                const primeiraMensagem = lista[0];
                this.dadosUnicos = {
                    description: primeiraMensagem.description,
                    task_uuid: primeiraMensagem.task_uuid,
                    started_task: moment(primeiraMensagem.started_task).format('DD/MM/YYYY HH:mm:ss'),
                    finished_task: moment(primeiraMensagem.finished_task).format('DD/MM/YYYY HH:mm:ss'),
                };
                console.log('dados', this.dadosUnicos)
            } else {
                this.dadosUnicos = {};
            }
        })
        this.loading = false
    }

    controlarTitulo(){
        return this.titulo
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: true,
            },
            {
                codigo: 'message',
                titulo: 'Mensagem',
                visivel: true,
            },
        ]);

    }

}
