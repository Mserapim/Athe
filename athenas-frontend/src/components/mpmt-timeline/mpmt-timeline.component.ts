import { AfterViewInit, ChangeDetectorRef, Component, ElementRef, Input, OnInit, TemplateRef, ViewChild } from "@angular/core";


interface EventoTimeline {
    templateCustomizado: any;
}

@Component({
    selector: 'mpmt-timeline',
    templateUrl: './mpmt-timeline.component.html',
    styleUrls: ['./mpmt-timeline.component.scss'],
    standalone: false
})
export class MpmtTimelineComponent implements AfterViewInit {
    @Input() events: EventoTimeline[] = [];
    @Input() templateEvento!: TemplateRef<any>;
    @ViewChild('inicioTimeline', { static: false }) inicioTimeline: ElementRef;
    @ViewChild('fimTimeline', { static: false }) fimTimeline: ElementRef;

    constructor(private cdRef: ChangeDetectorRef) {}

    ngAfterViewInit() {
        this.cdRef.detectChanges();
        this.calcularAltura();
    }

    private calcularAltura() {
        // Calcula a altura desde o primeiro até o último círculo para definir o comprimento da linha
        if (this.inicioTimeline && this.fimTimeline) {
            const inicio = this.inicioTimeline.nativeElement.offsetTop;
            const fim = this.fimTimeline.nativeElement.offsetTop;
            const altura = fim - inicio;

            const timelineContainer = this.inicioTimeline.nativeElement.closest('.timeline-container');
            if (timelineContainer) {
                timelineContainer.style.setProperty('--timeline-altura', `${altura}px`);
            }
        } else {
            setTimeout(() => this.calcularAltura(), 200);
        }
    }
}
    