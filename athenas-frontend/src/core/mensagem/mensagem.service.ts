import { Injectable } from '@angular/core';
import { IndividualConfig, ToastrService } from 'ngx-toastr';
import { Mensagem } from './mensagem.types';
import { NotificationToast } from 'layout/common/notification-toast/notification.toast.component';

@Injectable({
    providedIn: 'root',
})
export class MensagemService {
    constructor(private _toastrService: ToastrService) {}

    default(conteudo: string, desabilitarTimeOut?: boolean) {
        if (conteudo) {
            return this._toastrService.show(
                conteudo,
                '',
                MensagemService.obterConfiguracoesToastr(desabilitarTimeOut)
            ).toastId;
        }
    }

    info(conteudo: string, desabilitarTimeOut?: boolean) {
        if (conteudo) {
            return this._toastrService.info(
                conteudo,
                'Informação',
                MensagemService.obterConfiguracoesToastr(desabilitarTimeOut)
            ).toastId;
        }
    }

    processamento(conteudo: string, desabilitarTimeOut?: boolean) {
        if (conteudo) {
            return this._toastrService.info(
                conteudo,
                'Em Processamento!',
                MensagemService.obterConfiguracoesToastrParaProcessamento(
                    desabilitarTimeOut
                )
            ).toastId;
        }
    }

    sucesso(conteudo: string, desabilitarTimeOut?: boolean) {
        if (conteudo) {
            return this._toastrService.success(
                conteudo,
                'Sucesso',
                MensagemService.obterConfiguracoesToastr(desabilitarTimeOut)
            ).toastId;
        }
    }

    alerta(conteudo: string, desabilitarTimeOut?: boolean) {
        if (conteudo) {
            return this._toastrService.warning(
                conteudo,
                'Atenção',
                MensagemService.obterConfiguracoesToastr(desabilitarTimeOut)
            ).toastId;
        }
    }

    erro(conteudo: string, desabilitarTimeOut?: boolean) {
        if (conteudo) {
            return this._toastrService.error(
                conteudo,
                'Erro',
                MensagemService.obterConfiguracoesToastr(desabilitarTimeOut)
            ).toastId;
        }
    }

    fluxo(conteudo: string, desabilitarTimeOut?: boolean) {
        if (conteudo) {
            return this._toastrService.error(
                conteudo,
                'Ação não realizada',
                MensagemService.obterConfiguracoesToastr(desabilitarTimeOut)
            ).toastId;
        }
    }

    tipo(tipo: string, conteudo: string, desabilitarTimeOut?: boolean): number {
        let idMensagem: number;
        if (conteudo) {
            if (tipo == 'INFO') {
                idMensagem = this.sucesso(conteudo, desabilitarTimeOut);
            }
            if (tipo == 'WARN') {
                idMensagem = this.alerta(conteudo, desabilitarTimeOut);
            }
            if (tipo == 'ERROR') {
                idMensagem = this.erro(conteudo, desabilitarTimeOut);
            }
            if (tipo == 'FLUXO') {
                idMensagem = this.fluxo(conteudo, desabilitarTimeOut);
            }
        }
        return idMensagem;
    }

    exibirMensagens(listaMensagem: Mensagem[]): void {
        if (listaMensagem) {
            listaMensagem.forEach((mensagem: Mensagem) =>
                this.tipo(mensagem.tipoMessage, mensagem.message)
            );
        }
    }

    limparMensagens(listaIdMensagem: number[]) {
        listaIdMensagem.forEach((idMensagem) => {
            this._toastrService.clear(idMensagem);
        });
    }

    openNotificationToast(conteudo: string) {
        if (conteudo) {
            return this._toastrService.show(
                conteudo,
                'Nova Notificação',
                MensagemService.obterConfiguracoesNotificationToastr()
            ).toastId;
        }
    }

    private static obterConfiguracoesNotificationToastr(): Partial<IndividualConfig> {
        return {
            closeButton: true,
            timeOut: 50000,
            enableHtml: true,
            progressBar: true,
            progressAnimation: 'decreasing',
            disableTimeOut: false,
            positionClass: 'toast-top-right',
            toastComponent: NotificationToast,
        };
    }

    private static obterConfiguracoesToastr(
        desabilitarTimeOut?: boolean
    ): Partial<IndividualConfig> {
        return {
            closeButton: true,
            timeOut: 10000,
            enableHtml: true,
            progressBar: true,
            progressAnimation: 'decreasing',
            disableTimeOut: desabilitarTimeOut,
            positionClass: desabilitarTimeOut
                ? 'toast-bottom-right'
                : 'toast-top-right',
        };
    }

    private static obterConfiguracoesToastrParaProcessamento(
        desabilitarTimeOut?: boolean
    ): Partial<IndividualConfig> {
        return {
            closeButton: false,
            timeOut: 15000,
            enableHtml: true,
            progressBar: true,
            progressAnimation: 'decreasing',
            disableTimeOut: desabilitarTimeOut,
            positionClass: desabilitarTimeOut
                ? 'toast-bottom-right'
                : 'toast-top-right',
        };
    }
}
