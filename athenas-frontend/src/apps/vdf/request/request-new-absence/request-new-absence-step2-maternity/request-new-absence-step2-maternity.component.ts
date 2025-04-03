import { Component } from '@angular/core';
import {
    FormBuilder,
    FormControl,
    FormGroup,
    Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { addDay } from 'utils/add-day';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { PvfConfigRequestsPersonsDataSource } from 'datasources/pvf-config-requests-persons.datasource';
import { pvfConfigParamsDegreeKinshiptDataSource } from 'datasources/pvf-config-params-degree-kinshipt.datasource';
import { RequestNewAbsenceStep2Component } from '../request-new-absence-step2/request-new-absence-step2.component';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewAbsenceService } from '../request-new-absence.service';
import {
    RequestPersonNewComponent,
    RequestPersonNewComponentData,
} from '../../components/request-person-new/request-person-new.component';
import { MatDialog } from '@angular/material/dialog';
import {FuseConfirmationService} from "../../../../../@fuse/services/confirmation";
import {SelectItem} from "../../../../../utils/select-item";

@Component({
    selector: 'request-new-absence-step2-maternity',
    templateUrl: './request-new-absence-step2-maternity.component.html',
    standalone: false
})
export class RequestNewAbsenceStep2MaternityAbsencesComponent extends RequestNewAbsenceStep2Component {
    dataSourcePersons: PvfConfigRequestsPersonsDataSource;
    dataSourceDegreeKinshipt: pvfConfigParamsDegreeKinshiptDataSource;

    //classificacoes : SelectItem[] = [{label: 'Normal', value: 1}, {label: 'Antecipação', value: 2}]
    classificacoes : SelectItem[] = [{label: 'Normal', value: 1}]

    form = new FormGroup({
        file: new FormControl<File | null>(null, []),
        fileId: new FormControl<number | null>(null, [Validators.required]),
        dependent: new FormControl<number | Object | null>(null, []),
        start_date: new FormControl<Date | null>(null, []),
        days: new FormControl<number | null>(180, [Validators.required]),
        end_date: new FormControl<Date | null>(null, []),
        observation: new FormControl<boolean | null>(null, []),
        classificacao: new FormControl<number>(1, [Validators.required])
    });

    constructor(
        stepper: RequestStepperService,
        protected router: Router,
        public dialog: MatDialog,
        currentUserService: CurrentUserService,
        protected requestNewAbsenceService: RequestNewAbsenceService,
        protected confirmationService: FuseConfirmationService
    ) {
        super(stepper, router, currentUserService,
            requestNewAbsenceService, confirmationService, dialog);
    }

    protected getPayload() {
        if (this.form.value.classificacao === 1) {
            return {
                ...this.form.value,
                dependent: this.form.value.dependent['pk'],
                birth_certificate: this.form.value.fileId,
                substitutes: this.requestNewAbsenceService.substitutes,
            };
        } else {
            return {
                ...this.form.value,
                birth_certificate: this.form.value.fileId,
                substitutes: this.requestNewAbsenceService.substitutes,
            };
        }

    }

    displayFn(obj) {
        return obj?.name;
    }

    onSelectPerson($event) {
        this.form.controls['dependent'].setValue(
            $event?.option?.value || $event
        );

        const value = this.form.controls['dependent'].value as any;

        this.message = '';

        if (value.data_nascimento) {
            const splited = value.data_nascimento.split('-').map((x) => +x);

            const date = new Date(splited[0], --splited[1], splited[2]);
            this.form.controls['start_date'].setValue(date);
            this.form.controls['end_date'].setValue(
                addDay(date, this.form.value.days - 1)
            );
        } else {
            this.form.controls['end_date'].setValue(null);
            this.form.controls['start_date'].setValue(null);
            this.message =
                'Pessoa informada não tem data de nascimento informado';
        }
    }

    openPersonNew() {
        event?.stopPropagation();
        const dialogRef = this.dialog.open(RequestPersonNewComponent, {
            width: '90%',
            data: <RequestPersonNewComponentData>{
                close: (response) => {
                    if (response) this.onSelectPerson(response);
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
                // this.applyFilter();
            }
        });
    }

    onChangeSearch($event) {
        if (this.form.value.dependent instanceof Object) return;
        console.log(this.form.value.dependent);
        this.dataSourcePersons.load({
            keyword: this.form.value.dependent || undefined,
            page: 1,
            per_page: 10,
        });
    }

    ngOnInit() {
        this.dataSourceDegreeKinshipt =
            new pvfConfigParamsDegreeKinshiptDataSource();
        this.dataSourceDegreeKinshipt.load({ page: 1, per_page: 10 });
        this.dataSourcePersons = new PvfConfigRequestsPersonsDataSource();
        this.dataSourcePersons.load({ page: 1, per_page: 10 });
    }

    changeClassificacao() {
        this.form.patchValue({
            dependent: null,
            end_date: null,
            start_date: null
        })
    }

    desabilitarSalvar() {

        if (this.form.valid && this.form.value.classificacao === 1 && this.form.value.dependent != null) {
            return false;
        }

        if (this.form.valid && this.form.value.classificacao === 2) {
            return false;
        }

        return true;
    }
}
