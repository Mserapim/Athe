import { APP_INITIALIZER, NgModule, Optional, SkipSelf } from '@angular/core';
import { AuthModule } from 'core/auth/auth.module';
import { IconsModule } from 'core/icons/icons.module';
import { TranslocoCoreModule } from 'core/transloco/transloco.module';
import { NgxPermissionsModule } from 'ngx-permissions';
import { MensagemModule } from './mensagem/mensagem.module';
import { PermissaoService } from './permissao/permissao.service';
import { CurrentUserModule } from './current-user/current-user.module';
import { CurrentUserService } from './current-user/current-user.service';
import { NavegacaoAtualService } from './navegacao-atual/navegacao-atual.service';
import { PaginaTituloAtualService } from './pagina-titulo-atual/pagina-titulo-atual.service';

@NgModule({
    imports: [
        AuthModule,
        IconsModule,
        MensagemModule,
        TranslocoCoreModule,
        CurrentUserModule,
        NgxPermissionsModule.forRoot(),
    ],
    providers: [
        {
            // Carrega todas as permissões do usuário antes da inicialização da aplicação.
            provide: APP_INITIALIZER,
            useFactory: (currentUserService: CurrentUserService) =>
                function () {
                    currentUserService.load().then();
                },
            deps: [CurrentUserService],
            multi: true,
        },
        NavegacaoAtualService,
        PaginaTituloAtualService,
    ],
})
export class CoreModule {
    /**
     * Constructor
     */
    constructor(@Optional() @SkipSelf() parentModule?: CoreModule) {
        // Do not allow multiple injections
        if (parentModule) {
            throw new Error(
                'CoreModule has already been loaded. Import this module in the AppModule only.'
            );
        }
    }
}
