import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import {
    MatDialog,
    MatDialogRef,
    MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { PvfConfigRequestTypesDataSource } from 'datasources/pvf-config-requests-types.datasource';
import { PvfConfigRequestStatusDataSource } from 'datasources/pvf-config-requests-status.datasource';

export class RequestUserCreateDialogData {}

@Component({
    selector: 'request-user-create-dialog',
    templateUrl: 'request-user-create-dialog.html',
    standalone: false
})
export class RequestUserCreateDialog {
    public form = new FormGroup({
        nome: new FormControl<String | null>(null),
        cpf: new FormControl<String | null>(null),
        rg: new FormControl<String | null>(null),
        rg_orgao: new FormControl<String | null>(null),
        rg_uf: new FormControl<String | null>(null),
        rg_exp: new FormControl<String | null>(null),
        data_nascimento: new FormControl<String | null>(null),
        naturalidade: new FormControl<String | null>(null),
        sexo: new FormControl<String | null>(null),
        imigrante: new FormControl<String | null>(null),
        imigrante_condicao: new FormControl<String | null>(null),
    });

    requestTypesDataSource: PvfConfigRequestTypesDataSource;

    requestStatusDataSource: PvfConfigRequestStatusDataSource;

    constructor(
        public dialogRef: MatDialogRef<RequestUserCreateDialog>,
        @Inject(MAT_DIALOG_DATA) public data: RequestUserCreateDialogData
    ) {}

    ngOnInit() {
        this.requestTypesDataSource = new PvfConfigRequestTypesDataSource();
        this.requestStatusDataSource = new PvfConfigRequestStatusDataSource();
        this.loadRequestTypes().then();
        this.loadRequestStatus().then();
    }

    async loadRequestTypes() {
        this.requestTypesDataSource.load({
            page: 1,
            per_page: 10,
            year: 2022,
            month: 1,
        });
    }

    async loadRequestStatus() {
        this.requestStatusDataSource.load({
            page: 1,
            per_page: 10,
            year: 2022,
            month: 1,
        });
    }
}
