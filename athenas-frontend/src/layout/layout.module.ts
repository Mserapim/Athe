import { NgModule } from '@angular/core';
import { LayoutComponent } from 'layout/layout.component';
import { EmptyLayoutModule } from 'layout/layouts/empty/empty.module';
import { ClassicLayoutModule } from 'layout/layouts/vertical/classic/classic.module';
import { SettingsModule } from 'layout/common/settings/settings.module';
import { SharedModule } from 'shared/shared.module';
import { UsuarioModule } from './layouts/common/usuario/usuario.module';
import { ClockModule } from './layouts/common/clock/clock.module';
import { LayoutPadraoModule } from './layout-padrao/layout-padrao.module';
import { LayoutModulosModule } from './layout-modulos/layout-modulos.module';
import { LayoutNavegacaoModule } from './layout-navegacao/layout-navegacao.module';
import { NotificationsModule } from 'layout/common/notifications/notifications.module';

const DECLARATIONS = [LayoutComponent];

const layoutModules = [
    EmptyLayoutModule,
    ClassicLayoutModule,
    UsuarioModule,
    ClockModule,
    LayoutNavegacaoModule,
    LayoutPadraoModule,
    LayoutModulosModule,
    NotificationsModule,
];

@NgModule({
    declarations: DECLARATIONS,
    imports: [SharedModule, SettingsModule, ...layoutModules],
    exports: [LayoutComponent, ...layoutModules],
})
export class LayoutModule {}
