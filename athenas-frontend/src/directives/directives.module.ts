import { NgModule } from '@angular/core';
import { Route } from '@angular/router';
import { MpmtDebounceClickDirective } from './mpmt-debounce-click.directive';

const route: Route[] = [];

@NgModule({
    exports: [MpmtDebounceClickDirective],
    declarations: [MpmtDebounceClickDirective],
    providers: [],
    imports: [],
})
export class MpmtDirectivesModule {}