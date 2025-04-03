export interface Notification
{
    idNotificacao: string;
    nomeSistema: string;
    assunto: string;
    dataNotificacao: string;
    conteudo: string;
    idSistema: string;
    link?: string;
    read?: boolean;
}

export class Toast{
    id: number;
    notificacao: Notification;
}

export class ToastAction{
    id: number;
    touched: boolean;
    constructor(id?: number, touched?: boolean){
        this.id = id;
        this.touched = touched;
    }
}