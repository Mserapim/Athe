import {
    Component,
    EventEmitter,
    Input,
    OnDestroy,
    OnInit,
    Output,
    ViewEncapsulation,
} from '@angular/core';
import { BaseComponent } from 'shared/base-component/base-component';
import { Router } from '@angular/router';
import { CurrentUserService } from 'core/current-user/current-user.service';

@Component({
    selector: 'app-apps',
    templateUrl: './apps.component.html',
    encapsulation: ViewEncapsulation.None,
    exportAs: 'app-apps',
    standalone: false
})
export class AppsComponent extends BaseComponent implements OnInit, OnDestroy {
    aberto: boolean = false;

    constructor(
        private router: Router,
        public currentUserService: CurrentUserService
    ) {
        super();
    }

    ngOnInit() {}

    exibir() {
        this.aberto = true;
    }

    fechar() {
        this.aberto = false;
    }

    goApp(app: string) {
        // if (app == 'ATHENAS') this.router.navigate([`vdf/registro-de-ponto/`]);
        if (app == 'ATHENAS')
            window.open('https://athenas.mpmt.mp.br/', '_blank');
    }
}
