import { Component, HostListener, Inject, Input, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import {
    DomSanitizer,
    SafeResourceUrl,
    SafeUrl,
} from '@angular/platform-browser';

export class MpPdfPreviewComponentData {
    link: string;
    close: () => void;
}

@Component({
    selector: 'mp-pdf-preview',
    templateUrl: './mp-pdf-preview.component.html',
    standalone: false
})
export class MpPdfPreviewComponent {
    isLoading: boolean = true;
    srclink;

    constructor(
        sanitizer: DomSanitizer,
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        public payload: MpPdfPreviewComponentData
    ) {
        if (payload.link) {
            this.srclink = sanitizer.bypassSecurityTrustResourceUrl(
                payload.link
            );
        }
    }

    isFirefox(): boolean {
        const userAgent = window.navigator.userAgent.toLowerCase();
        return userAgent.indexOf('firefox') > -1;
    }

    public open(link: string): void {
        const dialogRef = this.dialog.open(MpPdfPreviewComponent, {
            width: '90%',
            height: '90%',
            data: <MpPdfPreviewComponentData>{
                link,
                close: () => {
                    dialogRef.close();
                },
            },
        });
    }

    goClose() {
        if (this.payload?.close) this.payload?.close();
        else this.dialog.closeAll();
    }

    getData() {
        //Adaptação feita pois estava ocorrendo um problema ao tentar baixar no firefox usando o mesmo srclink novamente.
        if (this.isFirefox()) {
            return null;
        }

        return this.srclink;
    }
}
