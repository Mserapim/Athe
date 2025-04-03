import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';

@Component({
    selector: 'request-new-regular-vacations-step4',
    templateUrl: './request-new-regular-vacations-step4.component.html',
    styleUrls: ['./request-new-regular-vacations-step4.component.scss'],
    standalone: false
})
export class RequestNewRegularVacationsStep4Component {
    firstFormGroup = this._formBuilder.group({
        firstCtrl: ['', Validators.required],
    });
    secondFormGroup = this._formBuilder.group({
        secondCtrl: ['', Validators.required],
    });
    isEditable = false;

    constructor(private _formBuilder: FormBuilder) {}
}
