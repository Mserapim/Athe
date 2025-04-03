import { Component, Inject, Input, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import {
    MAT_MOMENT_DATE_ADAPTER_OPTIONS,
    MomentDateAdapter,
} from '@angular/material-moment-adapter';
import {
    DateAdapter,
    MAT_DATE_FORMATS,
    MAT_DATE_LOCALE,
} from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { MY_FORMATS } from 'apps/app.component';
import {
    ApiRhPvfConfigRequestsTypeResponse,
    apiRhPvfConfigRequestsPersons,
} from 'api/rh/api-rh-pvf-config-requests-persons.service';
import { RhLocationsDataSource } from 'datasources/rh-locations.datasource';
import { RhConfigParamsImigrantConditionsDataSource } from 'datasources/rh-pvf-config-params-imigrant-conditions.datasource';
import { RhConfigParamsImigrantResidencesDataSource } from 'datasources/rh-pvf-config-params-imigrant-residences.datasource';

export class RequestPersonNewComponentData {
    close: (response?: ApiRhPvfConfigRequestsTypeResponse) => void;
}

@Component({
    selector: 'request-person-new',
    templateUrl: './request-person-new.component.html',
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
export class RequestPersonNewComponent implements OnInit {
    dataSourceLocations = new RhLocationsDataSource();
    imigrantConditionsDataSource =
        new RhConfigParamsImigrantConditionsDataSource();
    imigrantResidencesDataSource =
        new RhConfigParamsImigrantResidencesDataSource();

    form = new FormGroup({
        name: new FormControl<string>('', [Validators.required]),
        cpf: new FormControl<string>('', [Validators.required]),
        data_nascimento: new FormControl<Date>(null, [Validators.required]),
        municipio_naturalidade: new FormControl<{ id: number } | null>(null, [
            Validators.required,
        ]),
        sexo: new FormControl<{ value: 'M' | 'F' } | null>(null, [
            Validators.required,
        ]),
        immigrant_residence_time: new FormControl<{ value: number } | null>(
            null,
            [Validators.required]
        ),
        immigrant_entry_condition: new FormControl<{ value: number } | null>(
            null,
            [Validators.required]
        ),
    });

    sexos = [
        { value: 'F', name: 'Feminino' },
        { value: 'M', name: 'Masculino' },
    ];

    message: string = '';
    now = new Date();

    constructor(
        private route: ActivatedRoute,
        protected router: Router,
        private dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        public payload: RequestPersonNewComponentData
    ) {}

    ngOnInit() {
        this.loadLocations('');
        this.loadImigrantConditions('');
        this.loadImigrantResidences('');
    }

    protected async loadLocations(keyword) {
        this.dataSourceLocations.load({ keyword, per_page: 20 });
    }

    protected async loadImigrantConditions(keyword) {
        this.imigrantConditionsDataSource.load({ keyword, per_page: 20 });
    }

    protected async loadImigrantResidences(keyword) {
        this.imigrantResidencesDataSource.load({ keyword, per_page: 20 });
    }

    displayFnLocation(row: any): string {
        if (row) return `${row?.name}/${row?.sigla}`;
        else return '';
    }

    displayFnSexo(row: any): string {
        if (row) return `${row?.name}`;
        else return '';
    }

    displayFn(row: any): string {
        if (row) return `${row?.label}`;
        else return '';
    }

    close() {
        this.payload.close();
        this.dialog.closeAll();
    }

    async goConfirm() {
        if (!this.form.valid) return;

        this.message = '';
        try {
            const payload = {
                ...this.form.value,
                data_nascimento: this.form.value.data_nascimento
                    .toISOString()
                    ?.substring(0, 10),
                sexo: this.form.value.sexo?.value,
                immigrant_residence_time:
                    this.form.value.immigrant_residence_time?.value,
                immigrant_entry_condition:
                    this.form.value.immigrant_entry_condition?.value,
                municipio_naturalidade:
                    this.form.value.municipio_naturalidade?.id,
            };

            const response: any = await apiRhPvfConfigRequestsPersons(payload);
            await this.payload.close(response?.data?.data);
        } catch (e) {
            this.message = e?.response?.data?.message;
        }
    }
}
