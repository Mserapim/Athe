import { Component, EventEmitter, Input, Output, TemplateRef } from '@angular/core';

@Component({
    selector: 'mpmt-acordeao',
    templateUrl: './mpmt-acordeao.component.html',
    styleUrls: ['./mpmt-acordeao.component.scss'],
    standalone: false
})
export class MpmtAcordeaoComponent {
  @Input() titulo: string = '';
  @Input() subtitulo: string = '';
  @Input() templateRef: TemplateRef<any>;
  @Input() estaExpandido: boolean = false;
  @Output() toggle = new EventEmitter<void>();
}
