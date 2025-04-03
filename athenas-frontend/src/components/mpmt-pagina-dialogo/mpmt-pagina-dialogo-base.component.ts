import { Component, ViewChild } from '@angular/core';
import { MpmtPaginaDialogoComponent } from './mpmt-pagina-dialogo.component';

@Component({
    template: '',
})
export class MpmtPaginaDialogoBaseComponent {

    @ViewChild(MpmtPaginaDialogoComponent) modal?: MpmtPaginaDialogoComponent;

    constructor() {}

    public visivel: boolean = true
    callback: any 

    abrir(callback?: any) {
        this.visivel = true
        this.callback = callback
    } 

    fechar(){ 
        if(this.callback){
            this.callback()
        } 
        this.visivel = false
    }
    
    // Este método será chamado quando o evento fecharEvent for emitido pelo componente de diálogo
    onFecharEvent(): void {
        this.fechar();
    }
}
 