import {
    animate,
    keyframes,
    state,
    style,
    transition,
    trigger,
} from '@angular/animations';
import { Component, NgZone } from '@angular/core';
import { NotificationsService } from 'layout/common/notifications/notifications.service';
import { Toast, ToastPackage, ToastrService } from 'ngx-toastr';

@Component({
    selector: '[notificationtoast-toast-component]',
    templateUrl: './notification.toast.component.html',
    styles: [
        `
            :host {
                background-color: #39ba8c;
                position: relative;
                overflow: hidden;
                margin: 0 0 6px;
                padding: 0px 0px 0px 0px;
                width: 300px;
                border-radius: 3px 3px 3px 3px;
                color: #ffffff;
                pointer-events: all;
                cursor: pointer;
            }
            .btn-notification {
                -webkit-backface-visibility: hidden;
                -webkit-transform: translateZ(0);
            }
        `,
    ],
    animations: [
        trigger('flyInOut', [
            state('inactive', style({
                opacity: 0,
            })),
            transition('inactive => active', animate('400ms ease-out', keyframes([
                style({
                    transform: 'translate3d(100%, 0, 0) skewX(-30deg)',
                    opacity: 0,
                }),
                style({
                    transform: 'skewX(20deg)',
                    opacity: 1,
                }),
                style({
                    transform: 'skewX(-5deg)',
                    opacity: 1,
                }),
                style({
                    transform: 'none',
                    opacity: 1,
                }),
            ]))),
            transition('active => removed', animate('400ms ease-out', keyframes([
                style({
                    opacity: 1,
                }),
                style({
                    transform: 'translate3d(100%, 0, 0) skewX(30deg)',
                    opacity: 0,
                }),
            ]))),
        ]),
    ],
    preserveWhitespaces: false,
    standalone: false
})
export class NotificationToast extends Toast {
    touched: boolean = false;

    constructor(
        toastrService: ToastrService,
        toastPackage: ToastPackage,
        private notificationService: NotificationsService,
        ngZone?: NgZone
    ) {
        super(toastrService, toastPackage, ngZone);
    }

    action() {
        this.touched = true;
        this.remove();
    }

    ngOnDestroy() {
        this.notificationService.setToastId(
            this.toastPackage.toastId,
            this.touched
        );
        super.ngOnDestroy();
    }
}
