import { NgModule } from '@angular/core';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { FuseFullscreenModule } from '@fuse/components/fullscreen';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { FuseNavigationModule } from '@fuse/components/navigation';
import { LanguagesModule } from 'layout/common/languages/languages.module';
import { MessagesModule } from 'layout/common/messages/messages.module';
import { QuickChatModule } from 'layout/common/quick-chat/quick-chat.module';
import { SearchModule } from 'layout/common/search/search.module';
import { ShortcutsModule } from 'layout/common/shortcuts/shortcuts.module';
import { UserModule } from 'layout/common/user/user.module';
import { SharedModule } from 'shared/shared.module';
import { AtualizacaoCadastralEmailModule } from 'apps/vdf/atualizacao-cadastral/atualizacao-cadastral-email/atualizacao-cadastral-email.module';
import { UsuarioModule } from 'layout/layouts/common/usuario/usuario.module';
import { ClockModule } from 'layout/layouts/common/clock/clock.module';
import { AppsModule } from 'layout/layouts/common/apps/apps.module';
import { LayoutModulosComponent } from './layout-modulos.component';
import { SessaoModule } from 'core/sessao/sessao.module';
import { NotificationsModule } from 'layout/common/notifications/notifications.module';

@NgModule({ declarations: [LayoutModulosComponent],
    exports: [LayoutModulosComponent], imports: [RouterModule,
        MatButtonModule,
        MatDividerModule,
        MatIconModule,
        MatMenuModule,
        FuseFullscreenModule,
        FuseLoadingBarModule,
        FuseNavigationModule,
        LanguagesModule,
        MessagesModule,
        NotificationsModule,
        QuickChatModule,
        SearchModule,
        ShortcutsModule,
        UserModule,
        SharedModule,
        UsuarioModule,
        ClockModule,
        AppsModule,
        SessaoModule,
        AtualizacaoCadastralEmailModule], providers: [provideHttpClient(withInterceptorsFromDi())] })
export class LayoutModulosModule {}
