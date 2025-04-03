import { CollectionViewer, DataSource } from '@angular/cdk/collections';
import { ListPaginated } from 'api/@base/list-paginated';
import { BehaviorSubject, Observable } from 'rxjs';

export function baseDatasourceFactory<P, I, R extends ListPaginated<I>, X, Y>(
    service: (P) => Promise<R>
) {
    class GenericDataSource implements DataSource<I> {
        private resultsSubject = new BehaviorSubject<I[]>([]);
        private loadingSubject = new BehaviorSubject<boolean>(false);
        private totalSubject = new BehaviorSubject<number>(0);
        private perPageSubject = new BehaviorSubject<number>(10);
        private responseSubject = new BehaviorSubject<R>({} as any);
        public loading$ = this.loadingSubject.asObservable();
        public response$ = this.responseSubject.asObservable();
        public results$ = this.resultsSubject.asObservable();
        public total$ = this.totalSubject.asObservable();
        public perPage$ = this.totalSubject.asObservable();

        connect(collectionViewer: CollectionViewer): Observable<I[]> {
            return this.resultsSubject.asObservable();
        }

        disconnect(collectionViewer: CollectionViewer): void {
            this.resultsSubject.complete();
            this.loadingSubject.complete();
            this.totalSubject.complete();
            this.perPageSubject.complete();
        }

        async load(payload: P) {
            const response = await service(payload);
            this.responseSubject.next(response);
            this.totalSubject.next(response.total);
            this.perPageSubject.next(response.per_page);
            this.resultsSubject.next(response.results || []);
        }
    }

    return GenericDataSource;
}
