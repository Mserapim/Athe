import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtSelecaoComponent } from './mpmt-selecao.component';
import { Overlay } from '@angular/cdk/overlay';
import { MAT_AUTOCOMPLETE_SCROLL_STRATEGY } from '@angular/material/autocomplete';

export function autocompleteScrollStrategyFactory(overlay: Overlay) {
  return () => overlay.scrollStrategies.block();
}

const DECLARATIONS = [MpmtSelecaoComponent];

@NgModule({
    declarations: DECLARATIONS,
    providers: [
        ...DECLARATIONS,
        {
            provide: MAT_AUTOCOMPLETE_SCROLL_STRATEGY,
            useFactory: autocompleteScrollStrategyFactory,
            deps: [Overlay]
        }
    ],
    exports: DECLARATIONS,
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatInputModule,
        FormsModule,
        ReactiveFormsModule,
    ],
})
export class MpmtSelecaoModule {}
