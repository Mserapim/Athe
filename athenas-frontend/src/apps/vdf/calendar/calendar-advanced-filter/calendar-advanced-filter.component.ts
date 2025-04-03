import { Component } from '@angular/core';
import { PvfEmployePendingsDataSource } from 'datasources/pvf-employe-pendings.datasource';
import { PvfEmployeTeamDataSource } from 'datasources/pvf-employe-team.datasource';
import { PvfEventTypesDataSource } from 'datasources/pvf-event-types.datasource';

@Component({
    selector: 'app-calendar-advanced-filter',
    templateUrl: './calendar-advanced-filter.component.html',
    styleUrls: ['./calendar-advanced-filter.component.scss'],
    standalone: false
})
export class CalendarAdvancedFilterComponent {
    employeTeamDataSource: PvfEmployeTeamDataSource;
    eventTypesDataSource: PvfEventTypesDataSource;

    ngOnInit() {
        this.employeTeamDataSource = new PvfEmployeTeamDataSource();
        this.eventTypesDataSource = new PvfEventTypesDataSource();
        this.loadTeam();
        this.loadEventTypes();
    }

    async loadTeam() {
        await this.employeTeamDataSource.load({
            page: 1,
            per_page: 10,
            year: 2022,
            month: 1,
        });
    }

    async loadEventTypes() {
        await this.eventTypesDataSource.load({
            page: 1,
            per_page: 10,
            year: 2022,
            month: 1,
        });
    }
}
