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
import { LayoutPadraoComponent } from './layout-padrao.component';
import { LayoutPadraoUsuarioComponent } from '../layout-padrao-usuario/layout-padrao-usuario.component';
import { AvatarModule } from 'ngx-avatars';
import { LayoutModulosModule } from 'layout/layout-modulos/layout-modulos.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { LayoutPadraoCabecalhoComponent } from '../layout-padrao-cabecalho/layout-padrao-cabecalho.component';
import { NotificationsModule } from 'layout/common/notifications/notifications.module';

@NgModule({ declarations: [
        LayoutPadraoComponent,
        LayoutPadraoUsuarioComponent,
        LayoutPadraoCabecalhoComponent,
    ],
    exports: [
        LayoutPadraoComponent,
        LayoutPadraoUsuarioComponent,
        LayoutPadraoCabecalhoComponent,
    ], imports: [RouterModule,
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
        MatButtonModule,
        MatDividerModule,
        MatIconModule,
        MatMenuModule,
        SharedModule,
        AvatarModule,
        SharedModule,
        ClockModule,
        AppsModule,
        LayoutModulosModule,
        LayoutNavegacaoModule,
        AtualizacaoCadastralEmailModule], providers: [provideHttpClient(withInterceptorsFromDi())] })
export class LayoutPadraoModule {}
