import {
    Component,
    HostListener,
    OnDestroy,
    OnInit,
    ViewEncapsulation,
} from '@angular/core';
import { BaseComponent } from 'shared/base-component/base-component';
import {
    ApiRhPvfClockingLastBeatsItem,
} from 'api/rh/api-rh-pvf-clocking-last-beats.service';
import { Router } from '@angular/router';
import { CurrentUserService } from 'core/current-user/current-user.service';

@Component({
    selector: 'clock',
    templateUrl: './clock.component.html',
    encapsulation: ViewEncapsulation.None,
    exportAs: 'clock',
    standalone: false
})
export class ClockComponent extends BaseComponent implements OnInit, OnDestroy {
    time: Date = new Date();
    lastBeats: ApiRhPvfClockingLastBeatsItem[] = [];
    isMobile: boolean = false;

    constructor(
        private router: Router,
        public currentUserService: CurrentUserService
    ) {
        super();
    }

    showClockingBeat() {}

    ngOnInit() {
        this.checkScreenSize();
    }

    @HostListener('window:resize', ['$event'])
    onResize(event) {
        this.checkScreenSize();
    }

    private checkScreenSize() {
        this.isMobile = window.innerWidth < 768;
    }

    async loadLastBeat() {}

    goClocking() {
        this.router.navigate([`vdf/registro-de-ponto/`]);
    }
}
