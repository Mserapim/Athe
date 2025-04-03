import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { OverlayModule } from '@angular/cdk/overlay';
import { PortalModule } from '@angular/cdk/portal';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { NotificationsComponent } from './notifications.component';
import { NotificationToastModule } from 'layout/common/notification-toast/notification-toast.module';
import { NotificationsService } from './notifications.service';
import { CommonModule } from '@angular/common';
import { NotificacaoRxStompService } from './websocket/notificacao-rx-stomp.service';
import { NotificacaoRxStompServiceFactory } from './websocket/notificacao-rx-stomp-service-factory';
import { ToastrModule } from 'ngx-toastr';
import { InfiniteScrollModule } from 'ngx-infinite-scroll';

@NgModule({
    declarations: [NotificationsComponent],
    imports: [
        CommonModule,
        RouterModule,
        OverlayModule,
        PortalModule,
        MatButtonModule,
        MatIconModule,
        MatTooltipModule,
        NotificationToastModule,
        ToastrModule.forRoot(),
        InfiniteScrollModule,
    ],
    providers: [
        NotificationsService,
        {
            provide: NotificacaoRxStompService,
            useFactory: NotificacaoRxStompServiceFactory,
        },
    ],
    exports: [NotificationsComponent],
})
export class NotificationsModule {}
