import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { forkJoin, Observable } from 'rxjs';
import { MessagesService } from 'layout/common/messages/messages.service';
import { NavigationService } from 'core/navigation/navigation.service';
import { QuickChatService } from 'layout/common/quick-chat/quick-chat.service';
import { ShortcutsService } from 'layout/common/shortcuts/shortcuts.service';
import { NotificationsService } from 'layout/common/notifications/notifications.service';

@Injectable({
    providedIn: 'root',
})
export class InitialDataResolver  {
    /**
     * Constructor
     */
    constructor(
        private _messagesService: MessagesService,
        private _navigationService: NavigationService,
        private _notificationsService: NotificationsService,
        private _quickChatService: QuickChatService,
        private _shortcutsService: ShortcutsService
    ) {}

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Use this resolver to resolve initial mock-api for the application
     *
     * @param route
     * @param state
     */
    resolve(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ): Observable<any> {
        // Fork join multiple API endpoint calls to wait all of them to finish
        return forkJoin([
            this._navigationService.get(),
            this._messagesService.getAll(),
            this._quickChatService.getChats(),
            this._shortcutsService.getAll(),
        ]);
    }
}
