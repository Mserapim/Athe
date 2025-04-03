import { Component, OnInit, ViewChild } from '@angular/core';
import { useDownload } from 'api/@base/use-download';
import { apiReportRhPvfEmployeeScaleService } from 'api/report/api-report-rh-pvf-employee-scale.service';
import { PvfConfigServerShiftsWorkplacesDataSource } from 'datasources/pvf-config-server-shifts-workplaces.datasource';
import { PvfConfigServerShiftsEmployeesDataSource } from 'datasources/pvf-config-server-shifts-employees.datasource';
import { ApiRhPvfConfigEmployeesServiceResponseItem } from 'api/rh/api-rh-pvf-config-employees.service';
import { ApiRhConfigWorkplacesResponseItem } from 'api/rh/api-rh-config-worksplaces.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';
import { apiRhPvfConfigServerShiftsPermissionsTypes } from 'api/rh/api-rh-pvf-config-server-shifts-permisions-types.service';
import { apiRhLocations } from 'api/rh/api-rh-locations.service';

const nowString = new Date().toISOString();
const year = nowString.substring(0, 4);
const month = nowString.substring(5, 7);
const referenceStart = month + '/' + year;

@Component({
    selector: 'app-reports-server-shift',
    templateUrl: './reports-server-shift.component.html',
    styleUrls: ['../reports.component.scss'],
    standalone: false
})
export class ReportsServerShiftComponent implements OnInit {
    dataSourceEmployee = new PvfConfigServerShiftsEmployeesDataSource();
    dataSourceWorkplaces = new PvfConfigServerShiftsWorkplacesDataSource();
    message: string = '';
    isLoading = false;

    tipos = [];
    comarcasOpcoes: { label: string; value: number }[] = [];

    form = new FormGroup({
        tipo_filtro: new FormControl<'COMPETENCIA' | 'PERIODO'>('COMPETENCIA', []),
        inicio: new FormControl<Date | null>(null, []),
        fim: new FormControl<Date | null>(null, []),
        employee:
            new FormControl<ApiRhPvfConfigEmployeesServiceResponseItem | null>(
                null
            ),
        workplace: new FormControl<ApiRhConfigWorkplacesResponseItem | null>(
            null
        ),
        competencia: new FormControl<string | null>(referenceStart, []),
        reference: new FormControl<string | null>(referenceStart, []),
        tipo_plantao: new FormControl<number | null>(null),
        comarcas: new FormControl<number[]>([]),
    });

    constructor(private mpPdfPreviewComponent: MpPdfPreviewComponent) {}

    ngOnInit() {
        this.loadEmployees();
        this.loadWorkplaces();
        this.loadTipos();
        this.loadComarcas();
    }

    ngAfterViewInit() {}

    loadEmployees(keyword?: string) {
        this.dataSourceEmployee.load({ keyword, per_page: 12 });
    }

    loadWorkplaces(keyword?: string) {
        this.dataSourceWorkplaces.load({ keyword, per_page: 12 });
    }

    async loadTipos() {
        const { results } = await apiRhPvfConfigServerShiftsPermissionsTypes(
            {todos_tipos: true}
        );
        this.tipos = results;
    }

    async loadComarcas(keyword?: string) {
        const estado_MT = 79;
        const payload = {
            keyword: keyword || '',
            page: 1,
            per_page: 10,
            estado: estado_MT,
        };
    
        const { results } = await apiRhLocations(payload);
        this.comarcasOpcoes = results.map(comarca => ({
            label: comarca.name,
            value: comarca.id,
        }));
    }

    onComarcasSelecionadas(ids: number[]) {
        this.form.patchValue({ comarcas: ids });
    }
    
    filtrarComarcas(keyword: string) {
        this.loadComarcas(keyword);
    }

    displayFn(user: { name: string }): string {
        return user && user.name ? user.name : '';
    }

    get isValid() {
        return this.form.valid;
    }

    async download() {
        this.isLoading = true;
        const { uuid } = await apiReportRhPvfEmployeeScaleService({
            competence: this.form.value.tipo_filtro === 'COMPETENCIA' ? this.form.value.competencia : undefined,
            inicio: this.form.value.tipo_filtro === 'PERIODO' ? this.form.value.inicio : undefined,
            fim: this.form.value.tipo_filtro === 'PERIODO' ? this.form.value.fim : undefined,
            employee_id: this.form.value?.employee?.pk,
            workplace_id: this.form.value?.workplace?.pk,
            tipo_plantao: this.form.value?.tipo_plantao,
            comarcas: this.form.value?.comarcas,
        });
        try {
            const link = await useDownload(uuid, 0, 30, {
                automaticDownload: false,
            });

            this.mpPdfPreviewComponent.open(link);
        } finally {
            this.isLoading = false;
        }
    }
}
