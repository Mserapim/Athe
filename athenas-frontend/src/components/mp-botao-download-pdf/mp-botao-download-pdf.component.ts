import { Component, HostListener, Inject, Input, OnInit } from '@angular/core';

/** Ideia pausada
 * Objetivo é ter um botão que sempre que baixar o arquivo abre o preview do pdf
 *
 */
@Component({
    selector: 'mp-botao-download-pdf',
    templateUrl: './mp-botao-download-pdf.component.html',
    standalone: false
})
export class MpBotaoDownloadPdfComponent implements OnInit {
    @Input() label: string = 'Baixar';
    @Input() getFileIdFn: () => string;

    isLoading: boolean = true;

    constructor() {}

    ngOnInit() {}

    async download() {
        const uuid = this.getFileIdFn;
        console.log(uuid);
    }
}
