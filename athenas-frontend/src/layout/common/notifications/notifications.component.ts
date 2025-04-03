import {
    ChangeDetectionStrategy,
    ChangeDetectorRef,
    Component,
    Input,
    OnDestroy,
    OnInit,
    TemplateRef,
    ViewChild,
    ViewContainerRef,
    ViewEncapsulation,
} from '@angular/core';
import { Overlay, OverlayRef } from '@angular/cdk/overlay';
import { TemplatePortal } from '@angular/cdk/portal';
import { MatButton } from '@angular/material/button';
import { Subject, Subscription, takeUntil } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { ConteudoDialog } from './dialog/conteudo.component';
import { NotificationsService } from './notifications.service';
import { Notification, Toast, ToastAction } from './notifications.types';
import { NotificacaoRxStompService } from './websocket/notificacao-rx-stomp.service';
import { environment } from 'environments/environment';
import { MatTooltip } from '@angular/material/tooltip';
import moment from 'moment';
// import { MensagemService } from 'app/core/services/mensagem.service';
// import { EstadoSidebarDataService } from 'app/core/services/estado-sidebar-data.service';
import { MpmtBaseComponent } from 'components/mpmt-base-component/mpmt-base-component.component';
import { MensagemService } from 'core/mensagem/mensagem.service';
import { EstadoSidebarDataService } from 'core/estado-sidebar-data/estado-sidebar-data.service';
import { apiAdmNotificacoesHermes } from 'api/adm/api-adm-notificacoes-hermes.service';

@Component({
    selector: 'notifications',
    templateUrl: './notifications.component.html',
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.OnPush,
    exportAs: 'notifications',
    standalone: false
})
export class NotificationsComponent
    extends MpmtBaseComponent
    implements OnInit, OnDestroy
{
    @ViewChild('notificationsOrigin') private _notificationsOrigin: MatButton;
    @ViewChild('notificationsPanel')
    private _notificationsPanel: TemplateRef<any>;
    @ViewChild('tooltip') tooltip: MatTooltip;
    @Input() idComponent: string;

    toastAction: ToastAction;
    private subscription: Subscription;
    private subscriptionWebsocket: Subscription;

    menuLateralVisivel: boolean = true;

    link = environment.notificacoesURL;
    notifications: Notification[];
    toastQueue: Toast[] = [];
    items: any[] = [];
    receivedMessages: string[] = [];
    unreadCount: number = 0;
    novaNotificacao: boolean = false;
    private _overlayRef: OverlayRef;
    mensagem: string = 'Notificações';
    urlBase = environment.url_base;
    paginaAtual = 0;
    notificacoesPorPagina = 10;

    /**
     * Constructor
     */
    constructor(
        private _changeDetectorRef: ChangeDetectorRef,
        private _notificationsService: NotificationsService,
        private _overlay: Overlay,
        private _viewContainerRef: ViewContainerRef,
        private dialog: MatDialog,
        private rxStompService: NotificacaoRxStompService,
        private _mensagem: MensagemService,
        private _estadoSidebarService: EstadoSidebarDataService
    ) {
        super();
        this.subscription = this._notificationsService.toastId$.subscribe(
            (valor) => {
                this.toastAction = valor;
                this.openNotificationByToast(this.toastAction);
            }
        );
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Lifecycle hooks
    // -----------------------------------------------------------------------------------------------------

    /**
     * On init
     */
    ngOnInit(): void {
        this.consultarMenuLateralVisivel();
        this.subscriptionWebsocket = this.rxStompService
            .watch('/user/queue/greetings')
            .subscribe((res) => {
                let notificacao: Notification;
                try {
                    notificacao = JSON.parse(res.body);
                    this.mensagem =
                        notificacao.nomeSistema + ' - ' + notificacao.assunto;
                    if (
                        (!this.menuLateralVisivel &&
                            this.idComponent === 'header') ||
                        this.menuLateralVisivel
                    )
                        this.ativa(notificacao);
                } catch {
                    this.mensagem = res.body;
                    if (
                        (!this.menuLateralVisivel &&
                            this.idComponent === 'header') ||
                        this.menuLateralVisivel
                    )
                        this.ativa();
                }
            });
    }

    consultarMenuLateralVisivel() {
        this._estadoSidebarService.atualizarVisibilidadeSidebar$
            .pipe(takeUntil(this.unsubscribe))
            .subscribe((visivel: boolean) => {
                this.menuLateralVisivel = visivel;
            });
    }

    ngOnDestroy(): void {
        // Dispose the overlay
        if (this._overlayRef) {
            this._overlayRef.dispose();
        }
        super.ngOnDestroy();
        this.subscriptionWebsocket.unsubscribe;
        this.subscription.unsubscribe();
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    onMessage(message: any): void {
        this.items.push(message.body);
    }

    ativa(notificacao?: Notification): void {
        let toast = new Toast();
        this.novaNotificacao = true;
        toast.id = this._mensagem.openNotificationToast(this.mensagem);
        toast.notificacao = notificacao;
        this.toastQueue.push(toast);
        this._changeDetectorRef.markForCheck();
    }
    /**
     * Open the notifications panel
     */
    async openPanel() {
        this.paginaAtual = 0;
        this.notifications = [];

        this.onScroll();

        this.novaNotificacao = false;

        // Return if the notifications panel or its origin is not defined
        if (!this._notificationsPanel || !this._notificationsOrigin) {
            return;
        }

        // Create the overlay if it doesn't exist
        if (!this._overlayRef) {
            this._createOverlay();
        }

        // Attach the portal to the overlay
        this._overlayRef.attach(
            new TemplatePortal(this._notificationsPanel, this._viewContainerRef)
        );
    }

    onScroll() {
        this.paginaAtual += 1;
        this._notificationsService
            .listarNotificacoes(this.paginaAtual, this.notificacoesPorPagina)
            .then(
                (x) =>
                    (this.notifications = this.notifications.concat(x.results))
            );
    }
    /**
     * Close the messages panel
     */
    closePanel(): void {
        this._overlayRef.detach();
    }

    openDialog(notificacao: Notification): void {
        if (this.isOverlayAttached()) this.closePanel();
        let dataNotificacao = moment(notificacao.dataNotificacao).format(
            'DD/MM/YYYY HH:mm'
        );
        const dialogRef = this.dialog.open(ConteudoDialog, {
            data: {
                nomeSistema: notificacao.nomeSistema,
                assunto: notificacao.assunto,
                dataNotificacao: dataNotificacao,
                conteudo: notificacao.conteudo,
                idSistema: notificacao.idSistema,
            },
        });
    }

    openNotificationByToast(toastAction: ToastAction) {
        let index = this.toastQueue.findIndex(
            (toast) => toast.id === toastAction.id
        );
        if (toastAction.touched) {
            this.novaNotificacao = false;
            this._changeDetectorRef.markForCheck();
            let notificacao = this.toastQueue[index].notificacao;
            this.toastQueue.splice(index, 1);
            if (notificacao) this.openDialog(notificacao);
        } else {
            this.toastQueue.splice(index, 1);
        }
    }

    isOverlayAttached(): boolean {
        return this._overlayRef && this._overlayRef.hasAttached();
    }

    /**
     * Track by function for ngFor loops
     *
     * @param index
     * @param item
     */
    trackByFn(index: number, item: any): any {
        return item.idNotificacao || index;
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Private methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Create the overlay
     */
    private _createOverlay(): void {
        // Create the overlay
        this._overlayRef = this._overlay.create({
            hasBackdrop: true,
            backdropClass: 'fuse-backdrop-on-mobile',
            scrollStrategy: this._overlay.scrollStrategies.block(),
            positionStrategy: this._overlay
                .position()
                .flexibleConnectedTo(
                    this._notificationsOrigin._elementRef.nativeElement
                )
                .withLockedPosition(true)
                .withPush(true)
                .withPositions([
                    {
                        originX: 'start',
                        originY: 'bottom',
                        overlayX: 'start',
                        overlayY: 'top',
                    },
                    {
                        originX: 'start',
                        originY: 'top',
                        overlayX: 'start',
                        overlayY: 'bottom',
                    },
                    {
                        originX: 'end',
                        originY: 'bottom',
                        overlayX: 'end',
                        overlayY: 'top',
                    },
                    {
                        originX: 'end',
                        originY: 'top',
                        overlayX: 'end',
                        overlayY: 'bottom',
                    },
                ]),
        });

        // Detach the overlay from the portal on backdrop click
        this._overlayRef.backdropClick().subscribe(() => {
            this._overlayRef.detach();
        });
    }
}
