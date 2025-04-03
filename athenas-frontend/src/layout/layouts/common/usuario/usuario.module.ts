import { NgModule } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { SharedModule } from 'shared/shared.module';
import { AvatarModule } from 'ngx-avatars';
import { UsuarioComponent } from './usuario.component';

@NgModule({
    declarations: [UsuarioComponent],
    imports: [
        MatButtonModule,
        MatDividerModule,
        MatIconModule,
        MatMenuModule,
        SharedModule,
        AvatarModule,
    ],
    exports: [UsuarioComponent],
})
export class UsuarioModule {}
