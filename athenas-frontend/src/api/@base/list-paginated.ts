export class ListPaginated<T> {
    total: number;
    page: number;
    per_page: number;
    results: T[];
}
