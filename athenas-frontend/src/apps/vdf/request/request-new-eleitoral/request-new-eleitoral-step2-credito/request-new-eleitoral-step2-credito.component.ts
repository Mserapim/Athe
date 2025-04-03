import { Component } from '@angular/core';
import {
    FormControl,
    FormGroup, ValidationErrors,
    Validators,
} from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';
import { addDay } from 'utils/add-day';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { MatDialog } from '@angular/material/dialog';
import {FuseConfirmationService} from "../../../../../@fuse/services/confirmation";
import {gedUpload} from "../../../../../api/ged/api-ged-upload.service";
import {Documento} from "../../../../../components/mpmt-file-update/mpmt-file-update.component";
import {MatSnackBar} from "@angular/material/snack-bar";
import moment from "moment";
import {
    apiVdfSolicitacaoCreditoEleitoralCriarService
} from "../../../../../api/vdf/api-vdf-solicitacao-credito-dispensa-eleitoral-criar.service";
import {
    apiVdfSolicitacaoCreditoEleitoralDetalhes
} from "../../../../../api/vdf/api-vdf-solicitacao-credito-dispensa-eleitoral-detalhes.service";
import {
    apiVdfSolicitacaoCreditoEleitoralEditarService
} from "../../../../../api/vdf/api-vdf-solicitacao-credito-dispensa-eleitoral-editar.service";
import {useGedDownload} from "../../../../../api/@base/use-ged-download";
import {RequestNewEleitoralService} from "../request-new-eleitoral.service";
import {ConfigRequestsTiposEleitoralEnum} from "../../../../../enums/config-requests-tipos-eleitoral.enum";

@Component({
    selector: 'request-new-eleitoral-step2-credito',
    templateUrl: './request-new-eleitoral-step2-credito.component.html',
    standalone: false
})
export class RequestNewEleitoralStep2CreditoComponent {
    file = null;
    message: string;

    anexos: any[] = []
    anexos_carregados: Documento[] = []
    idSolicitacao: number;
    modoEdicao = false;

    obsRetorno: string = null;

    id: number = null;

    protected form: any = new FormGroup({
        file: new FormControl<number | null>(null, []),
        anexo: new FormControl<number | null>(null, [Validators.required]),
        data_inicio: new FormControl<Date | null>(new Date(), [
            Validators.required,
        ]),
        days: new FormControl<number | null>(1, [Validators.required, Validators.min(1), Validators.pattern('^[0-9]*$')]),
        data_fim: new FormControl<Date | null>(new Date(), [Validators.required]),
        observacao: new FormControl<String | null>(null, []),
        mode: new FormControl<'DAY' | 'HOUR'>('DAY', []),
    });

    constructor(
        protected stepper: RequestStepperService,
        protected router: Router,
        public dialog: MatDialog,
        currentUserService: CurrentUserService,
        protected confirmationService: FuseConfirmationService,
        private snackBar: MatSnackBar,
        private route: ActivatedRoute,
        protected service: RequestNewEleitoralService,
    ) {
        this.stepper.steps = ['Tipo de solicitação', 'Dados do formulário'];
        this.stepper.currentStep = 1;
        this.service.typeId = ConfigRequestsTiposEleitoralEnum.INCLUSAO_DIREITO;
    }

    ngOnInit() {
        this.onChangeDays(1);
        this.route.paramMap.subscribe(params => {
            const idSolicitacao = params.get('idSoliitacao')!
            if (idSolicitacao != null) {
                this.idSolicitacao = Number(idSolicitacao);
                this.modoEdicao = true;
                this.loadDados()
            }
        });

    }

    async loadDados() {
        const response = await apiVdfSolicitacaoCreditoEleitoralDetalhes({id: this.idSolicitacao});
        this.form.patchValue({
            anexo: response.anexo,
            data_inicio: moment(response.data_inicio, 'YYYY-MM-DD').toDate(),
            data_fim: moment(response.data_fim, 'YYYY-MM-DD').toDate(),
            observacao: response.observacao,
            days: response.dias
        })
        this.file = {name: response.nome_anexo}
        this.obsRetorno = response.obs_aprovador;
    }

    public async downloadAnexo() {
        await useGedDownload(this.form.get('anexo').value.toString());
    }

    async onFileInput($file) {
        this.file = $file.target.files[0];
        const response = await gedUpload({
            file: this.file,
            fileName: this.file.name,
        });

        this.form.get('anexo').setValue(response.data.file_id);
    }

    async goConfirm() {
        if(this.form.invalid) {
            return;
        }

        try {
            if (this.modoEdicao) {
                await apiVdfSolicitacaoCreditoEleitoralEditarService({
                    id: this.idSolicitacao,
                    data_inicio: moment(this.form.value.data_inicio).format('YYYY-MM-DD'),
                    data_fim:  moment(this.form.value.data_fim).format('YYYY-MM-DD'),
                    observacao: this.form.value.observacao,
                    anexo: this.form.value.anexo
                })
            } else {
                await apiVdfSolicitacaoCreditoEleitoralCriarService({
                    data_inicio: moment(this.form.value.data_inicio).format('YYYY-MM-DD'),
                    data_fim:  moment(this.form.value.data_fim).format('YYYY-MM-DD'),
                    observacao: this.form.value.observacao,
                    anexo: this.form.value.anexo
                })
            }

            this.router.navigate(['vdf/solicitacoes']);
        } catch (e) {
            this.exibirMensagem('Erro', e?.response?.data?.message);
            console.error(e);
            console.log(e)
        }


    }

    protected exibirMensagem(titulo: string, texto: string) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar']
        });
    }

    displayFn(obj) {
        return obj?.name;
    }

    onChangeMode($event) {
        this.onChangeStartDate(this.form.value.start_date);
    }

    onChangeStartDate($event) {
        this.form.value.data_inicio = $event;
        if (!this.form.value.data_inicio) return;
        if (this.form.value.mode == 'HOUR') {
            if (!this.form.value.data_inicio) return;
            this.form.value.data_fim = addDay($event, 0);
        } else {
            if (!this.form.value.days) return;
            this.form.value.data_fim = addDay(
                this.form.value.data_inicio,
                this.form.value.days - 1
            );
        }
    }

    onChangeDays($event) {
        this.form.value.days = $event;
        if (!this.form.value.data_inicio || !this.form.value.days) return;

        if (this.form.value.mode == 'HOUR') {
            this.form.value.data_fim = addDay(this.form.value.data_inicio, 0);
        } else {
            this.form.value.data_fim = addDay(
                this.form.value.data_inicio,
                this.form.value.days - 1
            );
        }
    }

    goBack() {
        this.router.navigate(['vdf/solicitacoes/novo/dispensa-eleitoral', 'step1']);
    }

    public getFormValidationErrors() {
        Object.keys(this.form.controls).forEach((key) => {
            const controlErrors: ValidationErrors = this.form.get(key).errors;
            if (controlErrors != null) {
                Object.keys(controlErrors).forEach((keyError) => {});
            }
        });
    }
}
