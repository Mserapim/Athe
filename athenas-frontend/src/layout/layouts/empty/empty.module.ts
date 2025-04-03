import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { SharedModule } from 'shared/shared.module';
import { EmptyLayoutComponent } from 'layout/layouts/empty/empty.component';

@NgModule({
    declarations: [EmptyLayoutComponent],
    imports: [RouterModule, FuseLoadingBarModule, SharedModule],
    exports: [EmptyLayoutComponent],
})
export class EmptyLayoutModule {}
