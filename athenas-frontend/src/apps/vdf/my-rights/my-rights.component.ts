import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { apiRhPvfMyRights } from 'api/rh/api-rh-pvf-my-rights.service';
import { apiRhPvfMyRightsAcquisitionPeriods } from 'api/rh/api-rh-pvf-my-rights-acquisition-periods.service';
import { apiRhPvfMyRightsAcquisitionPeriodsUsufructs } from 'api/rh/api-rh-pvf-my-rights-acquisition-periods-usufructs.service';
import {
    MyRightsDaysComponent,
    MyRightsDaysComponentData,
} from './my-rights-days/my-rights-days.component';
import { printDate } from 'utils/print-date';

@Component({
    selector: 'app-my-rights',
    templateUrl: './my-rights.component.html',
    styleUrls: ['./my-rights.component.scss'],
    standalone: false
})
export class MyRightsComponent implements OnInit {
    resultsMyRights = [];

    dataSourceMyRights = [];
    resultsMyRightsAcquisitionPeriods = null;
    resultsMyRightsAcquisitionPeriodsUsufructs = null;

    displayedColumnsMyRights: string[] = ['title', 'balance_days'];

    displayedColumnsMyRightsAcquisitionPeriods: string[] = [
        'group_period_name',
        'start_date_fruition',
        'start_date_acquisition',
        'end_date_acquisition',
        'days',
        'booked_days',
        'balance_available',
        'attachments',
    ];

    displayedColumnsMyRightsAcquisitionPeriodsUsufructs: string[] = [
        'status_name',
        'start_date',
        'end_date',
        'days',
    ];

    constructor(public dialog: MatDialog) {}

    ngOnInit() {}

    ngAfterViewInit() {
        this.loadMyRights();
        // this.openMyRightsAttachments(170436);
    }

    public openMyRightsAttachments(aquisitionPeriodId: number): void {
        const dialogRef = this.dialog.open(MyRightsDaysComponent, {
            width: '90%',
            data: <MyRightsDaysComponentData>{
                aquisitionPeriodId,
                close: () => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
                // this.applyFilter();
            }
        });
    }

    async loadMyRights() {
        const { results } = await apiRhPvfMyRights({});
        this.resultsMyRights = results;
    }

    async selectMyRights(groupId: number) {
        this.resultsMyRightsAcquisitionPeriodsUsufructs = null;
        const { results } = await apiRhPvfMyRightsAcquisitionPeriods({
            config: groupId,
        });
        this.resultsMyRightsAcquisitionPeriods = results;
    }

    async selectMyRightsAcquisitionPeriods(id: number) {
        const { results } = await apiRhPvfMyRightsAcquisitionPeriodsUsufructs({
            id,
        });
        if (!results) this.resultsMyRightsAcquisitionPeriodsUsufructs = [];
        else this.resultsMyRightsAcquisitionPeriodsUsufructs = results;
    }

    printDate = printDate;
}
