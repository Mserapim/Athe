// event-bus.service.ts
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable()
export class AtualizarExercicioCumulativoService {
    private ExercicioCumulativoSubject = new Subject<any>();

    emitEvent(event: string, data: any) {
        this.ExercicioCumulativoSubject.next({ event, data });
    }

    getEvent() {
        return this.ExercicioCumulativoSubject.asObservable();
    }
}