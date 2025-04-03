import { Component, ContentChild, EventEmitter, Input, Output, TemplateRef, ViewEncapsulation } from '@angular/core';
import { MpmtPaginaDialogoService } from './mpmt-pagina-dialogo.service';

@Component({
    selector: 'mpmt-pagina-dialogo',
    templateUrl: './mpmt-pagina-dialogo.component.html',
    standalone: false,
    encapsulation: ViewEncapsulation.None,
    styles: [`
        .overflow-y-auto {
            scrollbar-width: thin;
            scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
        }
        
        .overflow-y-auto::-webkit-scrollbar {
            width: 6px;
        }
        
        .overflow-y-auto::-webkit-scrollbar-track {
            background: transparent;
        }
        
        .overflow-y-auto::-webkit-scrollbar-thumb {
            background-color: rgba(156, 163, 175, 0.5);
            border-radius: 3px;
        }
    `]
})
export class MpmtPaginaDialogoComponent {

    @ContentChild('cabecalho', { static: false }) cabecalho?: TemplateRef<any>;
    @ContentChild('corpo', { static: false }) corpo?: TemplateRef<any>;
    @ContentChild('rodape', { static: false }) rodape?: TemplateRef<any>;

    @Input() permiteFechar: boolean = true;

    @Output() fecharEvent = new EventEmitter<void>();

    constructor(private mpmtPaginaDialogoService: MpmtPaginaDialogoService) {}

    fechar(): void {
        this.mpmtPaginaDialogoService.fechar();
    }

}