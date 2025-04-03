import { Component, Inject, SecurityContext } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";
import { DomSanitizer } from "@angular/platform-browser";
import { Notification } from "../notifications.types";
import { environment } from 'environments/environment';

const icone = `<mat-icon role="img" class="mat-icon icon-size-16 text-sky-500" data-mat-icon-type="svg">
<svg viewBox="0 0 24 24" fit="" height="100%" width="100%" preserveAspectRatio="xMidYMid meet" 
focusable="false">
<path d="M0 0h24v24H0z" fill="none"></path>
<path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 
2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM17 13l-5 5-5-5h3V9h4v4h3z">
</path></svg></mat-icon>`;


@Component({
    selector: 'conteudo',
    templateUrl: 'conteudo.component.html',
    standalone: false
})
export class ConteudoDialog {
  conteudo
  urlBase = environment.url_base;
  constructor(
    public dialogRef: MatDialogRef<ConteudoDialog>,
    @Inject(MAT_DIALOG_DATA) public data: Notification,
    private sanitized: DomSanitizer
  ) {
    let conteudo = this.data.conteudo;
    if (conteudo.includes("target=\"_blank\">Clique aqui</a>")) {
      conteudo = conteudo.replace("<div style=\"font-family: Tahoma, Arial, Helvetica, sans-serif; font-size: 10pt;\">", 
      "<div style=\"font-family: Tahoma, Arial, Helvetica, sans-serif;font-size: 10pt;text-align: center;\">");
      conteudo = conteudo.replace("<a ", '<a onclick=\"getElementById(\'btnFecharModalNotificacao\').click()\" ');
      conteudo = conteudo.replace("Clique aqui", icone);
      conteudo = conteudo.replace("</a> para baixar o arquivo.</p>", "<br>Baixar o arquivo</a></p><br>");  
    }
    let conteudoSemQuebrasDeLinha = conteudo.replace(/[\r\n]/g, "");
    this.conteudo = this.sanitized.bypassSecurityTrustHtml(conteudoSemQuebrasDeLinha);
  }

  onNoClick(): void {
    this.dialogRef.close();
  }
}