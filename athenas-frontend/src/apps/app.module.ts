import { ApplicationConfig, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ExtraOptions, PreloadAllModules, RouterModule } from '@angular/router';
import { FuseModule } from '@fuse';
import { FuseConfigModule } from '@fuse/services/config';
import { FuseMockApiModule } from '@fuse/lib/mock-api';
import { CoreModule } from 'core/core.module';
import { appConfig } from 'core/config/app.config';
import { LayoutModule } from 'layout/layout.module';
import { AppComponent } from 'apps/app.component';
import { appRoutes } from 'apps/app.routing';
import { FullCalendarModule } from '@fullcalendar/angular';
import { HashLocationStrategy, LocationStrategy } from '@angular/common';
import { MaterialModule } from '../shared/material/material.module';
import { MatMomentDateModule } from '@angular/material-moment-adapter';
import { mockApiServices } from 'core/mock-api';
import { PainelControleModule } from './painel-controle/painel-controle.module';
import { BaseModule } from './base/base.module';
import { MovimentacaoCarreiraModule } from './movimentacao-carreira/movimentacao-carreira.module';
import { DiariasModule } from './diarias/diarias.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { AnotacoesPessoaisModule } from './anotacoes-pessoais/anotacoes-pessoais.module';
import { GestaoPessoasModule } from './gestao-pessoas/gestao-pessoas.module';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';
import { PRIME_NG_LOCALE_PT_BR } from './pt-br';
import { PRIME_NG_THEME } from './prime-ng.preset';


const routerConfig: ExtraOptions = {
    preloadingStrategy: PreloadAllModules,
    scrollPositionRestoration: 'enabled',
};

@NgModule({
    providers: [
        { provide: LocationStrategy, useClass: HashLocationStrategy },
        provideAnimationsAsync(),
        providePrimeNG({
            translation: PRIME_NG_LOCALE_PT_BR,
            theme: {
                preset: PRIME_NG_THEME, 
                options: {
                    darkModeSelector: false || 'none'
                }
            },
        }),
    ],
    declarations: [AppComponent],
    imports: [
        MatMomentDateModule,
        BrowserModule,
        BrowserAnimationsModule,
        RouterModule.forRoot(appRoutes, routerConfig),

        // Fuse, FuseConfig & FuseMockAPI
        FuseModule,
        FuseConfigModule.forRoot(appConfig),
        FuseMockApiModule.forRoot(mockApiServices),

        // Core module of your application
        CoreModule,

        // Layout module of your application
        LayoutNavegacaoModule,
        LayoutModule,

        FullCalendarModule,
        MaterialModule,

        BaseModule,
        CoreModule,
        PainelControleModule,
        MovimentacaoCarreiraModule,
        DiariasModule,
        GestaoPessoasModule,
        AnotacoesPessoaisModule,
    ],
    bootstrap: [AppComponent],
})
export class AppModule {}
