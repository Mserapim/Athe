import { APP_INITIALIZER, NgModule, Optional, SkipSelf } from '@angular/core';
import { SessaoModuloService } from './sessao-modulo.service';

@NgModule({
    imports: [],
    providers: [SessaoModuloService],
    exports: [],
})
export class SessaoModule {}
