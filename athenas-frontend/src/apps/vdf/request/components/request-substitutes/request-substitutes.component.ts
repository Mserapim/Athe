import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CurrentUserService } from 'core/current-user/current-user.service';
import {
    apiRhPvfConfigRequestsDesignations,
    apiRhPvfConfigRequestsDesignationsItem,
} from 'api/rh/api-rh-pvf-config-requests-designations.service';
import { PvfConfigRequestsCandidateSubstitutesDataSource } from 'datasources/rh-pvf-config-requests-candidate-substitutes.datasource';
import moment from "moment";

@Component({
    selector: 'request-substitutes',
    templateUrl: './request-substitutes.component.html',
    styleUrls: ['./request-substitutes.component.scss'],
    standalone: false
})
export class RequestSubstitutesComponent {
    @Input() required: boolean = true;

    @Input() dates: {
        start_date: Date;
        end_date: Date;
        days: number;
    }[] = [];

    @Output('isValid') isValidOutput = new EventEmitter<boolean>();

    @Output('substitutes') substitutesOutput = new EventEmitter<
        {
            start_date: Date;
            end_date: Date;
            exercise: number;
            substitute: number;
            range_dates?: [Date, Date][];
        }[]
    >();

    protected message: string;
    candidatesDataSource: PvfConfigRequestsCandidateSubstitutesDataSource;
    exercises: apiRhPvfConfigRequestsDesignationsItem[];

    substitutes: {
        index: string;
        exercise: number;
        start_date: Date;
        end_date: Date;
        substitute?: number;
        employee: {
            pk: number;
            name: string;
        };
    }[] = [];

    constructor(private currentUserService: CurrentUserService) {}

    ngOnInit() {}

    ngOnChanges() {
        this.loadExercises().then((a) => {
            this.populateSubstitutes();
        });

        this.loadCandidates();
    }

    get isRequired() {
        return (
            this.currentUserService.currentUser?.is_substitutable == 'REQUIRED'
        );
    }

    async loadExercises() {
        const dates = this.dates.map((x) => {
            return {
                ...x,
                start_date: x.start_date.toISOString(),
                end_date: x.end_date.toISOString(),
            };
        });

        const { results } = await apiRhPvfConfigRequestsDesignations({
            dates,
        });
        this.exercises = results;
    }

    async loadCandidates() {
        this.candidatesDataSource =
            new PvfConfigRequestsCandidateSubstitutesDataSource();
        this.candidatesDataSource.load({ page: 1, per_page: 10 });
    }

    populateSubstitutes() {
        for (let exercise of this.exercises) {
            if (exercise?.range_dates) {
                for (let range of exercise.range_dates) {
                    let date = this.dates.filter(date => date.start_date === range[0]).shift()
                    this.substitutes.push({
                        index:new Date().getTime() + '',
                        exercise: exercise.pk,
                        start_date: range[0] ? moment(range[0]).toDate() : date.start_date,
                        end_date: range[1] ?moment(range[1]).toDate() : date.end_date,
                        employee: null,
                    });
                }
            } else {
                for (let date of this.dates) {
                    if (!date.start_date) continue;
                    this.substitutes.push({
                        index: new Date().getTime() + '',
                        exercise: exercise.pk,
                        end_date: date.end_date,
                        start_date: date.start_date,
                        employee: null,
                    });
                }
            }
        }
        this.emits();
    }

    changeStartDate(index2: string, $event) {
        let index = this.substitutes.findIndex((x) => {
            return x.index == index2;
        });

        if ($event.value) {
            this.substitutes[index].start_date = $event.value;
        } else {
            this.substitutes[index].start_date = undefined;
        }
        this.emits();
    }

    changeEndDate(index2: string, $event) {
        let index = this.substitutes.findIndex((x) => {
            return x.index == index2;
        });

        if ($event.value) {
            this.substitutes[index].end_date = $event.value;
        } else {
            this.substitutes[index].end_date = undefined;
        }
        this.emits();
    }

    add(exercise: number) {
        this.substitutes.push({
            index: new Date().getTime() + '',
            end_date: null,
            exercise,
            start_date: null,
            employee: null,
        });
        this.emits();
    }

    remove(index: string) {
        this.substitutes = this.substitutes.filter((x) => x.index != index);
        this.emits();
    }

    getSubstitutesByExercise(exercise) {
        return this.substitutes.filter((x) => exercise == x.exercise);
    }

    displayFn(obj) {
        return obj?.name;
    }

    onSelectCandidate($event) {
        this.emits();
    }

    onSearchCandidates($event) {
        this.candidatesDataSource.load({
            keyword: $event.target.value,
            page: 1,
            per_page: 10,
        });
    }

    emits() {
        const x = this.substitutes
            .map((x) => {
                return {
                    start_date: x.start_date,
                    end_date: x.end_date,
                    exercise: x.exercise,
                    substitute: x?.employee?.pk,
                };
            })
            .filter((x) => {
                return (
                    x.start_date &&
                    x.end_date &&
                    x.exercise &&
                    x.substitute &&
                    x.start_date <= x.end_date
                );
            });

        this.isValidOutput.emit(!this.isRequired || this.isValid);

        this.substitutesOutput.emit(x);
    }

    get isValid() {
        if (!this.required) return true;
        const found = this.substitutes.find((x) => {
            return (
                !x?.employee?.pk ||
                !x.start_date ||
                !x.end_date ||
                !x.exercise ||
                x.start_date > x.end_date
            );
        });

        return !found;
    }
}
