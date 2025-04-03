import { Component } from '@angular/core';
import {
    FormBuilder,
    FormControl,
    FormGroup,
    Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
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

@Component({
    selector: 'request-new-absence-step2-marriage',
    templateUrl: './request-new-absence-step2-marriage.component.html',
    standalone: false
})
export class RequestNewAbsenceStep2MarriageComponent extends RequestNewAbsenceStep2Component {
    form = new FormGroup({
        file: new FormControl<File | null>(null, []),
        fileId: new FormControl<number | null>(null, [Validators.required]),
        person: new FormControl<number | Object | null>(null, [
            Validators.required,
        ]),
        start_date: new FormControl<Date | null>(null, [Validators.required]),
        days: new FormControl<number | null>(8, [Validators.required]),
        end_date: new FormControl<Date | null>(null, [Validators.required]),
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
        return {
            ...this.form.value,
            person: this.form.value.person['pk'],
            marriage_certificate: this.form.value.fileId,
            substitutes: this.requestNewAbsenceService.substitutes,
        };
    }

    dataSourcePersons: PvfConfigRequestsPersonsDataSource;
    dataSourceDegreeKinshipt: pvfConfigParamsDegreeKinshiptDataSource;
    displayFn(obj) {
        return obj?.name;
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

    onSelectPerson($event) {
        this.form.controls['person'].setValue($event?.option?.value || $event);
    }

    onChangeSearch($event) {
        if (this.form.value.person instanceof Object) return;
        console.log(this.form.value.person);
        this.dataSourcePersons.load({
            keyword: this.form.value.person || undefined,
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

    ngAfterInitView() {
        this.onChangeStartDate(new Date());
    }
}

//     file = null;
//     fileId: number = null;
//     dataSourcePersons: PvfConfigRequestsPersonsDataSource;
//     keyword = 'name';

//     form = new FormGroup({
//         file: new FormControl<File | null>(null, []),
//         fileId: new FormControl<number | null>(null, [Validators.required]),
//         dependent: new FormControl<number | null>(null, [Validators.required]),
//         is_incoming_tax: new FormControl<boolean | null>(null, [
//             Validators.required,
//         ]),
//         dependent_type: new FormControl<number | null>(null, [
//             Validators.required,
//         ]),
//         capacity: new FormControl<boolean | null>(null, [Validators.required]),
//         is_childcare_assistence: new FormControl<boolean | null>(null, [
//             Validators.required,
//         ]),
//         start: new FormControl<Date | null>(null, [Validators.required]),
//         days: new FormControl<number | null>(8, [Validators.required]),
//         end: new FormControl<Date | null>(null, [Validators.required]),
//         observation: new FormControl<boolean | null>(null, []),
//     });

//     constructor(
//         private _snackBar: MatSnackBar,
//         private requestStepperService: RequestStepperService,
//         private _formBuilder: FormBuilder,
//         private router: Router
//     ) {
//         this.requestStepperService.currentStep = 2;
//     }

//     ngOnInit() {
//         this.dataSourcePersons = new PvfConfigRequestsPersonsDataSource();
//         this.dataSourcePersons.load({ page: 1, per_page: 10 });
//     }

//     async onFileInput($file) {
//         this.file = $file.target.files[0];
//         const response = await gedUpload({
//             file: this.file,
//             fileName: this.file.name,
//         });

//         this.form.value.file = $file.target.files[0];
//         this.form.controls['fileId'].setValue(response.data.file_id);
//         this.fileId = response.data.file_id;
//     }

//     onSelectPerson($event) {
//         this.form.controls['dependent'].setValue($event.pk);
//     }

//     onChangeSearch($event) {
//         this.dataSourcePersons.load({
//             keyword: $event,
//             page: 1,
//             per_page: 10,
//         });
//     }

//     onChangeStartDate($event) {
//         this.form.value.start = $event;
//         if (!this.form.value.start || !this.form.value.days) return;
//         this.form.value.end = addDay(
//             this.form.value.start,
//             this.form.value.days
//         );
//     }

//     onChangeDays($event) {
//         this.form.value.days = $event;
//         if (!this.form.value.start || !this.form.value.days) return;
//         this.form.value.end = addDay(
//             this.form.value.start,
//             this.form.value.days
//         );
//     }
//     goBack() {
//         this.router.navigate(['vdf/solicitacoes/novo/afastamentos', 'step1']);
//     }

//     async goNext() {
//         try {
//             const response = await pvfRequestsAbsencesPaternityAbsencesService({
//                 is_incoming_tax: this.form.value.is_incoming_tax,
//                 dependent_type: this.form.value.dependent_type,
//                 is_childcare_assistence:
//                     this.form.value.is_childcare_assistence,
//                 capacity: this.form.value.capacity,
//                 birth_certificate: this.form.value.fileId,
//                 start_date: this.form.value.start,
//                 end_date: this.form.value.end,
//                 dependent: this.form.value.dependent,
//                 observation: '',
//             });

//             this.router.navigate(['vdf/solicitacoes']);
//         } catch (e) {
//             console.log('asdfasdfasdf', e.response);
//             this.showMessage(e.response?.data?.message);
//         }
//     }

//     showMessage(message: string) {
//         this._snackBar.open(message);
//     }
// }
