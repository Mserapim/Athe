import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { apiRhPvfConfigServerShiftsPermissionsTypes } from 'api/rh/api-rh-pvf-config-server-shifts-permisions-types.service';
import { addDay } from 'utils/add-day';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { PvfConfigRequestsPersonsDataSource } from 'datasources/pvf-config-requests-persons.datasource';
import { PvfConfigServerShiftsEmployeesDataSource } from 'datasources/pvf-config-server-shifts-employees.datasource';
import { PvfConfigServerShiftsWorkplacesDataSource } from 'datasources/pvf-config-server-shifts-workplaces.datasource';
import { Router } from '@angular/router';
import { apiRhPvfScalesServerShiftsPostService } from 'api/rh/api-rh-pvf-scales-server-shifts-post.service';
import {
    ApiRhConfigWorkplacesResponseItem,
    apiRhConfigWorkplaces,
} from 'api/rh/api-rh-config-worksplaces.service';
import {
    DateAdapter,
    MAT_DATE_FORMATS,
    MAT_DATE_LOCALE,
} from '@angular/material/core';
import { MY_FORMATS } from 'apps/app.component';
import {
    MAT_MOMENT_DATE_ADAPTER_OPTIONS,
    MomentDateAdapter,
} from '@angular/material-moment-adapter';
import {catchError, debounceTime, distinctUntilChanged, Subject, switchMap} from "rxjs";
import {gedUpload} from "../../../../api/ged/api-ged-upload.service";
import {MatSnackBar} from "@angular/material/snack-bar";

export class ServerShiftNewComponentData {
    close: () => void;
}

@Component({
    selector: 'app-server-shift-new',
    templateUrl: './server-shift-new.component.html',
    styleUrls: ['./server-shift-new.component.scss'],
    providers: [
        { provide: MAT_DATE_LOCALE, useValue: 'pt-BR' },
        // `MomentDateAdapter` can be automatically provided by importing `MomentDateModule` in your
        // application's root module. We provide it at the component level here, due to limitations of
        // our example generation script.
        {
            provide: DateAdapter,
            useClass: MomentDateAdapter,
            deps: [MAT_DATE_LOCALE, MAT_MOMENT_DATE_ADAPTER_OPTIONS],
        },
        { provide: MAT_DATE_FORMATS, useValue: MY_FORMATS },
    ],
    standalone: false
})
export class ServerShiftNewComponent implements OnInit {
    dataSourceEmployee: PvfConfigServerShiftsEmployeesDataSource;
    dataSourceWorkplaces: PvfConfigServerShiftsWorkplacesDataSource;

    workplaces: ApiRhConfigWorkplacesResponseItem[];
    message: string;
    keywordPerson: string;
    keywordWorkplace: string;

    types = [];

    private searchSubject = new Subject<string>();

    file = null;
    fileId: number = null;

    form = new FormGroup({
        employee: new FormControl<{ pk: number } | null>(null, [
            Validators.required,
        ]),
        workplace: new FormControl<{ pk: number } | null>(null, [
            Validators.required,
        ]),
        type: new FormControl<number | null>(null, [Validators.required]),
        start: new FormControl<Date | null>(new Date(), [Validators.required]),
        days: new FormControl<number | null>(1, [Validators.required]),
        end: new FormControl<Date | null>(new Date(), [Validators.required]),
        file: new FormControl<File | null>(null, []),
        fileId: new FormControl<number | null>(null, []),
        observation: new FormControl<string | null>(null, [])
    });

    constructor(
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        public payload: ServerShiftNewComponentData,
        private router: Router,
        private _snackBar: MatSnackBar
    ) {
        this.dataSourceEmployee =
            new PvfConfigServerShiftsEmployeesDataSource();
        this.dataSourceWorkplaces =
            new PvfConfigServerShiftsWorkplacesDataSource();

        this.onChangeSearchEmployee('');
        // this.onChangeSearchWorkplaces('');

        this.searchSubject.pipe(
            debounceTime(300), // Ajuste o tempo de debounce conforme necessário
            distinctUntilChanged(),
            switchMap(keyword => this.loadWorkplaces(keyword)), // Use switchMap para cancelar requisições anteriores
            catchError(err => {
                console.error(err);
                return [];
            })
        ).subscribe(results => this.workplaces = results);
    }

    ngOnInit() {}

    ngAfterViewInit() {
        this.loadTypes();
        this.loadWorkplaces();
    }

    private loadWorkplaces(keyword?) {
        return apiRhConfigWorkplaces({ keyword }).then(response => response.results);
    }

    onSearch(keyword: string) {
        this.searchSubject.next(keyword);
    }

    // onChangeSearchWorkplaces($event) {
    //     this.dataSourceWorkplaces.load({
    //         keyword: $event,
    //         page: 1,
    //         per_page: 10,
    //     });
    // }

    async loadTypes() {
        const { results } = await apiRhPvfConfigServerShiftsPermissionsTypes(
            {}
        );
        this.types = results;
    }

    onChangeStartDate($event) {
        this.form.value.start = $event;
        if (!this.form.value.start || !this.form.value.days) return;
        this.form.value.end = addDay(
            this.form.value.start,
            this.form.value.days - 1
        );
    }

    onChangeDays($event) {
        this.form.value.days = $event;
        if (!this.form.value.start || !this.form.value.days) return;
        this.form.value.end = addDay(
            this.form.value.start,
            this.form.value.days - 1
        );
    }

    onSelectEmployee($event) {
        // console.log($event);
        // this.form.value.familyId = $event.pk;
        this.form.controls['employeeId'].setValue($event.pk);
        // console.log(this.form.value);
    }

    onSelectWorkplace($event) {
        // console.log($event);
        // this.form.value.familyId = $event.pk;
        this.form.controls['workplaceId'].setValue($event.pk);
        // console.log(this.form.value);
    }

    onChangeSearchEmployee($event) {
        this.dataSourceEmployee.load({
            keyword: $event,
            page: 1,
            per_page: 10,
        });
    }

    displayFn(user: { name: string }): string {
        return user && user.name ? user.name : '';
    }

    displayServidor(user: { name: string, matricula:number }): string {
        return user && user.name ? `${user.matricula} - ${user.name}`: '';
    }

    async goConfirm() {
        this.message = '';
        try {
            const response = await apiRhPvfScalesServerShiftsPostService({
                // owner: number;
                workplace: this.form.value.workplace?.pk,
                type_shift: this.form.value.type,
                employee: this.form.value.employee?.pk,
                days: this.form.value.days,
                start_date: this.form.value.start,
                end_date: this.form.value.end,
                anexo: this.form.value.fileId,
                observacao: this.form.value.observation
            });
            this.payload.close();
        } catch (e) {
            if (e?.response?.data?.message)
                this.message = e?.response?.data?.message;
            else this.message = 'erro inesperado ao salvar';
        }
    }

    goBack() {
        this.router.navigate(['vdf/server-shifts']);
    }

    async onFileInput($file) {
        if ($file.target.files[0]?.type === 'application/pdf') {
            this.file = $file.target.files[0];
            const response = await gedUpload({
                file: this.file,
                fileName: this.file.name,
            });

            this.form.value.file = $file.target.files[0];
            this.form.value.fileId = response.data.file_id;
            this.fileId = response.data.file_id;
            this.form.patchValue({
                fileId: response.data.file_id,
            });
        } else {
            this.showMessage('Escolha um anexo do tipo .pdf');
        }
    }


    showMessage(mensagem: string) {
        this._snackBar.open(mensagem, '', {
            duration: 4000,
            panelClass: ['custom-snackbar'],
            verticalPosition: 'top',
        });
    }

    desabilitarSalvar() {
        if(this.form.valid && this.form.value.type != 3) {
            return false;
        }

        if(this.form.valid && this.form.value.type == 3 && this.form.value.fileId && this.form.value.observation) {
            return false;
        }

        return true;
    }
}
