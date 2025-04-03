import { Component, Input } from '@angular/core';
import { CalendarOptions } from '@fullcalendar/core'; // useful for typechecking
import dayGridPlugin from '@fullcalendar/daygrid';
import { apiRhPvfEventsService } from 'api/rh/api-rh-pvf-events';
import { apiRhPvfEventTypesService } from 'api/rh/api-rh-pvf-event-types.service';
import { apiRhPvfEmployeTeamsService } from 'api/rh/api-rh-pvf-employe-teams.service';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import ptBrLocale from '@fullcalendar/core/locales/pt-br';
import $ from 'jquery';
import { addDay } from 'utils/add-day';
import interactionPlugin from '@fullcalendar/interaction';

@Component({
    selector: 'app-calendar',
    templateUrl: './calendar.component.html',
    styleUrls: ['./calendar.component.scss'],
    standalone: false,
})
export class CalendarComponent {
    @Input() exibirFiltros?: boolean = true;
    @Input() class?: string = '';
    displayedMonth: number; // Armazena o mês exibido atualmente (baseado em zero)
    displayedYear: number; // Armazena o ano exibido atualmente

    public events = [];
    public eventsMobile = [];
    public eventTypes = [];
    public employees = [];
    public calendarOptions: CalendarOptions | any;
    public selectedDate: Date | string;
    public eventsFiltered = [];
    private lastMonth: number | null = null; // Armazena o último mês carregado
    private lastYear: number | null = null; // Armazena o último ano carregado

    data: any = {};

    form = new FormGroup({
        year: new FormControl<number>(new Date().getFullYear()),
        month: new FormControl<number>(undefined),
        employee_ids: new FormControl<number[]>(undefined),
        event_type_ids: new FormControl<number[]>(undefined),
        keyword: new FormControl<string>(undefined),
    });

    constructor(private fb: FormBuilder) {}

    ngOnInit() {
        this.buildCalendarOptions();
        this.loadEventTypes();
        this.loadEmployeeTeams();
    }

    buildEventsFiltered() {
        if (!this.selectedDate) this.eventsFiltered = [];
        this.eventsFiltered = this.events.filter((x) => {
            return (
                (x.start <= this.selectedDate && x.end > this.selectedDate) ||
                (x.start == this.selectedDate && x.end == this.selectedDate)
            );
        });
    }

    buildCalendarOptions() {
        let thiz = this;
        this.calendarOptions = <CalendarOptions | any>{
            initialView: 'dayGridMonth',
            plugins: [dayGridPlugin, interactionPlugin],
            locale: ptBrLocale,
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth',
            },
            views: {
                dayGridMonth: {
                    titleFormat: {
                        year: 'numeric',
                        month: '2-digit',
                    },
                },
            },
            defaultAllDay: true,
            datesSet: async function (dateInfo) {
                const middleDate = new Date(
                    (dateInfo.start.getTime() + dateInfo.end.getTime()) / 2
                );
                const month = middleDate.getMonth();
                const year = middleDate.getFullYear();
                if (thiz.lastMonth !== month || thiz.lastYear !== year) {
                    thiz.lastMonth = month;
                    thiz.lastYear = year;
                    await thiz.loadCalendar(middleDate);
                }
            },
            dayCellDidMount: function (info, b) {
                $(info.el).find('.fc-daygrid-day-frame').append(`<div style='
                position: absolute;
                height: 100%;
                width: 100%;
                top: 0px;
                cursor: pointer;
                opacity: 0.0;
                background: antiquewhite;
                z-index: 1000;
                '></div>`);
                $(info.el).on('click', function () {
                    thiz.selectedDate = new Date(info.date)
                        .toISOString()
                        .split('T')[0];
                    thiz.buildEventsFiltered();
                });
            },
            eventDidMount: function (info, b) {
                $(info.el).attr('title', info?.event?.title);
            },
            editable: true,
            events: [],
        };
    }

    async applyFilter() {
        const currentDate = new Date();
        await this.loadCalendar(currentDate);
    }

    async loadCalendar(date: Date) {
        let eventosCombinados = [];
        let count = 0;

        const year = date.getFullYear();
        const month = date.getMonth() + 1;

        const payload = {
            ...this.form.value,
            year: year,
            month: month,
        };
        const { results } = await apiRhPvfEventsService(payload);
        eventosCombinados = eventosCombinados.concat(results);

        this.events = eventosCombinados.map((event) => {
            const builded = { ...event } as any;
            if (event.end) {
                let endDate = new Date(event.end);
                endDate = addDay(endDate, 1);
                builded.end = endDate.toISOString().split('T')[0];
            } else {
                let startDate = new Date(event.start);
                startDate = addDay(startDate, 0);
                builded.end = startDate.toISOString().split('T')[0];
            }

            builded.groupId = event.event_type;
            if ((event.event_type = 1005)) {
                builded.id = +count;
            } else {
                builded.id = +event.pk;
            }
            const cor = this.TABELA_DE_CORES.find(
                (x) => x.value == builded.event_type
            );
            if (cor) builded.backgroundColor = cor.backgroundColor;
            count++;
            return builded;
        });

        function distinct(array: any[]) {
            return array.filter(
                (thing, i, arr) =>
                    arr.findIndex((t) => t?.id === thing?.id) === i
            );
        }

        this.eventsMobile = distinct(
            this.events.flatMap((x) => {
                const dateArray = new Array();
                const start = new Date(x.start);
                const end = new Date(x.end);
                end.setHours(0, 0, 0, 0);
                let currentDate = start;
                currentDate.setHours(0);
                while (currentDate < end) {
                    const event = {
                        id: new Date(currentDate).toISOString(),
                        start: addDay(currentDate, 1),
                        backgroundColor: '#3788d8',
                    };

                    dateArray.push(event);

                    currentDate = addDay(currentDate, 1);
                }
                return dateArray;
            })
        );
        this.buildEventsFiltered();
    }

    async loadEventTypes() {
        const { results: eventTypes } = await apiRhPvfEventTypesService({
            page: 1,
        });
        this.eventTypes = eventTypes;
    }

    async loadEmployeeTeams() {
        const { results: employees } = await apiRhPvfEmployeTeamsService({
            page: 1,
        });
        this.employees = employees;
    }

    TABELA_DE_CORES = [
        {
            backgroundColor: '#f26e6e',
            label: 'Aniversário',
            value: 1005,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Ausência - Casamento (Gala)',
            value: 33,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Ausência - Doação de Sangue',
            value: 31,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Ausência - Falecimento (Luto)',
            value: 35,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Ausência - Paternidade/Tutoria ou Adoção',
            value: 34,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Doença em pessoa da família',
            value: 11,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Licença - Atividade política',
            value: 16,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Licença - Capacitação ou especialização',
            value: 17,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Licença - Interesse particular',
            value: 18,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Licença Maternidade/Adoção',
            value: 12,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Tratamento de Saúde até 15 dias - Servidor',
            value: 9,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Tratamento de saúde até 30 dias - Membro',
            value: 37,
        },
        {
            backgroundColor: '#f26e6e',
            label: 'Tratamento de saúde junta médica',
            value: 10,
        },
        {
            backgroundColor: '#f97708',
            label: 'Concurso de Estagiários',
            value: 9012,
        },
        {
            backgroundColor: '#f97708',
            label: 'Concurso Promotor Substituto',
            value: 9011,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Doação de Sangue',
            value: 9013,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Folga de Aniversário',
            value: 9003,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Folga Eleitoral',
            value: 9004,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Folgas Compensatórias de Membros',
            value: 9007,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Plantão de Recesso Forense - Membros ',
            value: 9008,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Plantão (Servidores)',
            value: 9005,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Recesso de Estagiário',
            value: 9010,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Recesso Forense ',
            value: 9002,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Recesso Residentes',
            value: 9014,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Férias Individuais',
            value: 9001,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Férias Regulamentares',
            value: 9000,
        },
        {
            backgroundColor: '#3F4756',
            label: 'Licença Prêmio',
            value: 9009,
        },
        {
            backgroundColor: '#6ef273',
            label: 'Entrega Folha Ponto',
            value: 1002,
        },
        {
            backgroundColor: '#6ef273',
            label: 'Entrega Teletrabalho',
            value: 1001,
        },
        {
            backgroundColor: '#3788d8',
            label: 'Feriados',
            value: 1003,
        },
        {
            backgroundColor: 'brown',
            label: 'Substitutos',
            value: 1004,
        },
        {
            backgroundColor: '#A77E2F',
            label: 'Plantão',
            value: 4,
        },
    ];
}
