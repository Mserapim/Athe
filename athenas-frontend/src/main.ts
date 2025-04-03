import { ApplicationConfig } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from 'apps/app.module';
import { providePrimeNG } from 'primeng/config';


platformBrowserDynamic()
    .bootstrapModule(AppModule)
    .catch((err) => console.error(err));
