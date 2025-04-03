import { CollectionViewer, DataSource } from '@angular/cdk/collections';
import { MatDialog } from '@angular/material/dialog';
import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';
import { BehaviorSubject, Observable } from 'rxjs';
import { pvfRequestsService } from 'services/pvf/requests.service';

// class ListPaginated {
//     total: number;
//     page: string;
//     per_page: string;
//     results: PvfRequest[];
// }

class PvfRequest {
    approver: number;
    approver_name: string;
    date: string;
    employee: number;
    employee_name: string;
    pk: number;
    portal_request_type: number;
    status: number;
    status_name: string;
    step_current: number;
    step_current_name: string;
    type_of_request: string;
}

export class RequestsDataSource implements DataSource<PvfRequest> {
    private requestsSubject = new BehaviorSubject<PvfRequest[]>([]);
    private loadingSubject = new BehaviorSubject<boolean>(false);
    private totalSubject = new BehaviorSubject<number>(0);
    private perPageSubject = new BehaviorSubject<number>(10);
    private responseSubject = new BehaviorSubject<ListPaginated<PvfRequest>>(
        new ListPaginated()
    );
    public loading$ = this.loadingSubject.asObservable();
    public response$ = this.responseSubject.asObservable();
    public total$ = this.totalSubject.asObservable();
    public perPage$ = this.totalSubject.asObservable();

    public getCurrentRequests(): PvfRequest[] {
        return this.requestsSubject.value;
    }

    connect(collectionViewer: CollectionViewer): Observable<PvfRequest[]> {
        return this.requestsSubject.asObservable();
    }

    disconnect(collectionViewer: CollectionViewer): void {
        this.requestsSubject.complete();
        this.loadingSubject.complete();
        this.totalSubject.complete();
        this.perPageSubject.complete();
    }

    async load(
        payload: {
            keyword?: string;
            page?: number;
            per_page: number;
            request_type?: number[];
            status?: number[];
        } = {
            page: 1,
            per_page: 10,
        }
    ) {
        const response = await pvfRequestsService(payload);
        this.responseSubject.next(response.data);
        this.totalSubject.next(response.data.total);
        this.perPageSubject.next(payload.per_page);
        this.requestsSubject.next(response.data.results);
    }
}
