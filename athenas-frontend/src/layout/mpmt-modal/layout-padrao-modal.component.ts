import {Component, EventEmitter, Input, Output} from '@angular/core';


export interface ModalButton {
    label: string;
    action: () => void;
    disabled?: () => boolean;
    color?: string;
    backgroundColor?: string;
}

@Component({
    selector: 'layout-padrao-modal',
    templateUrl: './layout-padrao-modal.component.html',
    styleUrls: ['./layout-padrao-modal.component.scss'],
    standalone: false
})
export class LayoutPadraoModalComponent {
    @Input() title: string = 'Título do Modal';
    @Input() buttons: ModalButton[] = [];
    @Input() alignButtons: string = 'justify-end';
    @Input() customHeaderButtons: any;

    @Output() close = new EventEmitter<void>();


    closeModal(): void {
        this.close.emit();
    }
}
