import { NgModule } from '@angular/core';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { LayoutNavegacaoService } from './layout-navegacao.service';

@NgModule({ declarations: [],
    exports: [], imports: [RouterModule], providers: [LayoutNavegacaoService, provideHttpClient(withInterceptorsFromDi())] })
export class LayoutNavegacaoModule {}
