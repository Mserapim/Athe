import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { MatTable } from '@angular/material/table';
import { RequestNewHorizontalProgressionsService } from '../request-new-horizontal-progressions.service';

@Component({
    selector: 'request-new-horizontal-progressions-step2',
    templateUrl: './request-new-horizontal-progressions-step2.component.html',
    standalone: false
})
export class RequestNewHorizontalProgressionsStep2Component {
    @ViewChild(MatTable) table: MatTable<any>;

    documents: any[] = [];

    displayedColumns: string[] = ['description', 'originalName', 'id'];

    isLoading: boolean = false;

    file: any;

    constructor(
        private stepper: RequestStepperService,
        private router: Router,
        protected service: RequestNewHorizontalProgressionsService
    ) {
        stepper.currentStep = 1;
        this.service.message = '';
    }

    ngOnInit() {
        if (!this.service.selectedCurrent || !this.service.selectedNext || this.service.termo_aceite == false) {
            this.goBack();
        }
    }

    get isValid() {
        return (
            this.documents.length > 0 &&
            this.service.selectedCurrent &&
            this.service.selectedNext &&
            this.service.termo_aceite == true
        );
    }

    removeItem(id: number) {
        this.documents = this.documents.filter((x) => x.id != id);
        this.table.renderRows();
        this.service.message = '';
    }

    async onFileInput($file) {
        this.file = $file.target.files[0];
        const response = await gedUpload({
            file: this.file,
            fileName: this.file.name,
        });
        this.documents.push({
            id: new Date().getTime() + '',
            description: '',
            fileId: response.data.file_id,
            originalName: this.file.name,
        });

        this.table.renderRows();
        this.service.message = '';
    }

    goBack() {
        this.service.message = '';
        this.router.navigate([
            'vdf/solicitacoes/progressao-horizontal/',
            'step1',
        ]);
    }

    async goConfirm() {
        try {
            this.isLoading = true;
            if (!this.documents.every((doc) => doc.description.trim() !== '')) {
                this.service.message =
                    'A descrição do arquivo deve ser preenchida.';
                return;
            }

            this.service.documents = this.documents.map((x) => {
                return {
                    name: x.description,
                    attachment_id: x.fileId,
                };
            });
            await this.service.goConfirm();

            if (this.service.message) {
                return;
            }
            this.goRequests();
        } catch (e) {
        } finally {
            this.isLoading = false;
        }
    }

    public goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }
}
