import { Component } from '@angular/core';
import { RequestNewElectoralSlackComponent } from '../request-new-electoral-slack/request-new-electoral-slack.component';

@Component({
    selector: 'request-new-trainees-contest',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestNewTraineesContextComponent extends RequestNewElectoralSlackComponent {
    title = 'Solicitação de Concurso de estagiários';
}
