import {  Injectable } from '@angular/core';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';

@Injectable()
export class MpmtPaginaDialogoService {

    ref: DynamicDialogRef | undefined;

    constructor(public dialogService: DialogService) {}

    abrir(clazz): DynamicDialogRef<any> {
        this.ref = this.dialogService.open(clazz, { 
            data: {},
            modal:true,
            closeOnEscape: false,
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
        });

        return this.ref;
    }

    fechar() {
        if (this.ref) {
            this.ref.close();
        }
    }
}