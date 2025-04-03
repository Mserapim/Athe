import { Component, ElementRef, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import {
    apiRhPvfConfigRequestsDesignations,
    apiRhPvfConfigRequestsDesignationsItem,
} from 'api/rh/api-rh-pvf-config-requests-designations.service';
import { RequestNewVactionsService } from '../request-new-vacations.service';
import { PvfConfigRequestsCandidateSubstitutesDataSource } from 'datasources/rh-pvf-config-requests-candidate-substitutes.datasource';
import moment from 'moment';
import {
    FuseConfirmationConfig,
    FuseConfirmationService,
} from '../../../../../@fuse/services/confirmation';

@Component({
    selector: 'request-new-vacations-step3',
    templateUrl: './request-new-vacations-step3.component.html',
    standalone: false
})
export class RequestNewVacationsStep3Component {
    protected message: string;

    private configConfirmar: FuseConfirmationConfig = {
        title: 'Substituto não selecionado',
        message:
            'Atenção! Foi identificado que não possui substituto para a designação. Deseja informar um substituto?',
        icon: {
            show: true,
            name: 'heroicons_outline:exclamation',
            color: 'warn',
        },
        actions: {
            confirm: {
                show: true,
                label: 'Informar',
            },
            cancel: {
                show: true,
                label: 'Não informar',
            },
        },
        dismissible: false,
    };

    candidatesDataSource: PvfConfigRequestsCandidateSubstitutesDataSource;

    exercises: apiRhPvfConfigRequestsDesignationsItem[] = [];

    isLoading: boolean = false;

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

    @ViewChild('substitutos') selecaoSubstitutos: ElementRef;

    constructor(
        public currentUserService: CurrentUserService,
        public requestStepperService: RequestStepperService,
        public router: Router,
        public service: RequestNewVactionsService,
        public confirmationService: FuseConfirmationService
    ) {
        this.requestStepperService.currentStep = 2;

        // this.requestNewVactionsService.usufructs_in = [
        //     {
        //         start_date: new Date(),
        //         end_date: addDay(new Date(), 10),
        //     },
        //     {
        //         start_date: addDay(new Date(), 30),
        //         end_date: addDay(new Date(), 40),
        //     },
        // ];
    }

    ngOnInit() {
        if (!this.service?.usufructs_in?.length) this.goBack();

        this.loadExercises().then((a) => {
            this.populateSubstitutes();
        });

        this.loadCandidates();
    }

    async loadExercises() {
        let dates: any[] = this.service.usufructs_in || [];
        console.log(dates);
        dates = dates
            .filter((x) => x.start_date)
            .map((x) => {
                return {
                    ...x,
                    start_date: x.start_date.toISOString(),
                    end_date: x.end_date.toISOString(),
                };
            });

        const { results } = await apiRhPvfConfigRequestsDesignations({
            dates: dates,
        });
        this.exercises = results;
    }

    async loadCandidates() {
        this.candidatesDataSource =
            new PvfConfigRequestsCandidateSubstitutesDataSource();
        this.candidatesDataSource.load({ page: 1, per_page: 10 });
    }

    populateSubstitutes() {
        console.log(this.exercises);
        for (let exercise of this.exercises) {
            if (exercise?.range_dates) {
                for (let range of exercise.range_dates) {
                    let usufuct = this.usufructs
                        .filter(
                            (usufruct1) => usufruct1.start_date === range[0]
                        )
                        .shift();
                    this.substitutes.push({
                        index: (this.substitutes.length + 1).toString(),
                        exercise: exercise.pk,
                        start_date: range[0]
                            ? moment(range[0]).toDate()
                            : usufuct.start_date,
                        end_date: range[1]
                            ? moment(range[1]).toDate()
                            : usufuct.end_date,
                        employee: null,
                    });
                }
            } else {
                for (let usufuct of this.usufructs) {
                    if (!usufuct.start_date) continue;
                    this.substitutes.push({
                        index: (this.substitutes.length + 1).toString(),
                        exercise: exercise.pk,
                        end_date: usufuct.end_date,
                        start_date: usufuct.start_date,
                        employee: null,
                    });
                }
            }
        }
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
    }

    add(exercise: number) {
        this.substitutes.push({
            index: (this.substitutes.length + 1).toString(),
            end_date: null,
            exercise,
            start_date: null,
            employee: null,
        });
    }

    remove(index: string) {
        this.substitutes = this.substitutes.filter((x) => x.index != index);
    }

    getSubstitutesByExercise(exercise) {
        return this.substitutes.filter((x) => exercise == x.exercise);
    }

    displayFn(obj) {
        return obj?.name;
    }

    onSelectCandidate($event, substitute) {
        console.log($event, substitute);
    }

    onSearchCandidates($event) {
        this.candidatesDataSource.load({
            keyword: $event.target.value,
            page: 1,
            per_page: 10,
        });
    }

    goBack() {
        this.router.navigate(['vdf/solicitacoes/novo/ferias', 'step2']);
    }

    async goNext(validarSubstitutos: boolean) {
        if (validarSubstitutos === true) {
            this.validSubstitutes();
        } else {
            try {
                this.isLoading = true;
                this.service.substitutes = this.substitutes.map((x) => {
                    if (x.employee)
                        return {
                            start_date: x.start_date,
                            end_date: x.end_date,
                            exercise: x.exercise,
                            substitute: x.employee.pk,
                        };
                });
                this.removeElementoNull();
                const response = await this.service.confirm();
                this.goRequests();
            } catch (e) {
                this.message = e?.response?.data?.message;
            } finally {
                this.isLoading = false;
            }
        }
    }

    removeElementoNull() {
        this.service.substitutes = this.service.substitutes.filter(
            (element) => {
                return element !== null && element !== undefined;
            }
        );
        if (this.service.substitutes.length === 0) {
            this.service.substitutes = [];
        }
    }

    goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }

    public get isValid() {
        return true;
    }

    get usufructs() {
        return this.service.usufructs_in;
    }

    private validSubstitutes() {
        let modalConfirm;

        let membroAdmSuperior =
            this.currentUserService.currentUser.group_details
                .filter(
                    (group) =>
                        group.name === 'mpmt-perfil-vdf-administracao-superior'
                )
                .shift();

        if (membroAdmSuperior) {
            let substitutoNaoSelecionado = false;
            for (let substitute of this.substitutes) {
                if (
                    substitute.employee === null ||
                    Object.keys(substitute.employee).length === 0
                ) {
                    substitutoNaoSelecionado = true;
                    modalConfirm = this.confirmationService.open(
                        this.configConfirmar
                    );
                    break;
                }
            }

            if (substitutoNaoSelecionado === true) {
                modalConfirm.afterClosed().subscribe((result) => {
                    if (result === 'confirmed') {
                        this.selecaoSubstitutos.nativeElement.focus();
                    } else {
                        this.goNext(false);
                    }
                });
            } else {
                this.goNext(false);
            }
        } else {
            this.goNext(false);
        }
    }
}
