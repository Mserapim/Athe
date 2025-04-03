import { NgModule } from '@angular/core';
import { CommonModule, formatDate } from '@angular/common';

// Material Form Controls
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule } from '@angular/material/select';
import { MatSliderModule } from '@angular/material/slider';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
// Material Navigation
import { MatMenuModule } from '@angular/material/menu';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
// Material Layout
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatListModule } from '@angular/material/list';
import { MatStepperModule } from '@angular/material/stepper';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTreeModule } from '@angular/material/tree';
// Material Buttons & Indicators
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatBadgeModule } from '@angular/material/badge';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import {
    DateAdapter,
    MAT_DATE_FORMATS,
    MAT_DATE_LOCALE,
    MatNativeDateModule,
    MatRippleModule,
    NativeDateAdapter,
} from '@angular/material/core';
// Material Popups & Modals
import { MatBottomSheetModule } from '@angular/material/bottom-sheet';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
// Material Data tables
import {
    MatPaginatorIntl,
    MatPaginatorModule,
} from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
// Service Paginator Translate to Portuguese Brasil.
import { MatPaginatorService } from './material-paginator.service';
// import {
// MAT_MOMENT_DATE_FORMATS,
// MomentDateAdapter,
// MAT_MOMENT_DATE_ADAPTER_OPTIONS,
// MatMomentDateModule,
// } from '@angular/material-moment-adapter';

// import 'moment/locale/pt-br';
// import 'moment/locale/en';
import {
    // MAT_MOMENT_DATE_ADAPTER_OPTIONS,
    // MAT_MOMENT_DATE_FORMATS,
    MatMomentDateModule,
    // MomentDateAdapter,
} from '@angular/material-moment-adapter';

/**
 * Este módulo contém TODOS os módulos do angular material para ser usado no projeto.
 * Assim, não é preciso fazer nenhum import de biblioteca do angular material.
 * Instrução de uso: Ao adicionar o módulo SharedModule, você já estará adicionando
 * os módulos do angular material.
 */

const MATERIAL_MODULES = [
    MatAutocompleteModule,
    MatCheckboxModule,
    MatDatepickerModule,
    MatMomentDateModule,
    MatFormFieldModule,
    MatInputModule,
    MatRadioModule,
    MatSelectModule,
    MatSliderModule,
    MatSlideToggleModule,
    MatMenuModule,
    MatSidenavModule,
    MatToolbarModule,
    MatCardModule,
    MatDividerModule,
    MatExpansionModule,
    MatGridListModule,
    MatListModule,
    MatStepperModule,
    MatTabsModule,
    MatTreeModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatBadgeModule,
    MatChipsModule,
    MatFormFieldModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatProgressBarModule,
    MatRippleModule,
    MatBottomSheetModule,
    MatDialogModule,
    MatSnackBarModule,
    MatTooltipModule,
    MatPaginatorModule,
    MatSortModule,
    MatTableModule,
];

// import 'moment/locale/pt-br';

// export const MY_FORMATS = {
//     parse: {
//         dateInput: 'MM/YYYY',
//     },
//     display: {
//         dateInput: 'MM/YYYY',
//         monthYearLabel: 'MMM YYYY',
//         dateA11yLabel: 'LL',
//         monthYearA11yLabel: 'MMMM YYYY',
//     },
// };

@NgModule({
    declarations: [],
    imports: [CommonModule, ...MATERIAL_MODULES],
    providers: [
        { provide: MatPaginatorIntl, useClass: MatPaginatorService },
        // { provide: MAT_DATE_LOCALE, useValue: 'pt-BR' },
        // { provide: MAT_DATE_FORMATS, useValue: MY_FORMATS },
        // { provide: MAT_DATE_FORMATS, useValue: MAT_MOMENT_DATE_FORMATS },
        // {
        //     provide: DateAdapter,
        //     useClass: MomentDateAdapter,
        //     deps: [MAT_DATE_LOCALE, MAT_MOMENT_DATE_ADAPTER_OPTIONS],
        // },
        // { provide: MAT_DATE_FORMATS, useValue: MY_FORMATS },
    ],
    exports: [...MATERIAL_MODULES],
})
export class MaterialModule {}

// class PickDateAdapter extends NativeDateAdapter {
//     format(date: Date, displayFormat: Object): string {
//         console.log('teste', date.toISOString());
//         if (displayFormat === 'input') {
//             return formatDate(date, 'dd-MM-yyyy', this.locale);
//         } else {
//             return date.toDateString();
//         }
//     }
// }
