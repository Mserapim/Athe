import { Component, EventEmitter, Input, OnChanges, OnInit } from '@angular/core';

@Component({
    selector: 'mpmt-form-base',
    templateUrl: './mpmt-form-base.component.html',
    standalone: false,
})
export class MpmtFormBaseComponent  {

    @Input('titulo') titulo?: string = ""
    @Input('mensagemErro') mensagemErro?: string = ""

}
