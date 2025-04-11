Ext._define('rh.socialsecurity.EmploymentBondGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.socialsecurity.EmploymentBondWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 70, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Empregador', dataIndex: 'employer', id: 'autoExpandColumn', sortable: true},
                    {header: 'Previdência', dataIndex: 'pension_system_display', width: 70, sortable: true},
                    {header: 'Início', dataIndex: 'begin_date', width: 75, renderer: Ext.util.Format.dateRenderer('d/m/Y'), sortable: true},
                    {header: 'Término', dataIndex: 'end_date', width: 75, renderer: Ext.util.Format.dateRenderer('d/m/Y'), sortable: true},
                    {header: 'Deduções', dataIndex: 'deduction', width: 70, sortable: true},
                    {header: 'Tempo líquido', dataIndex: 'liquid_days', width: 80, sortable: true},
                    {header: 'Tempo Bruto', dataIndex: 'raw_days', width: 80, sortable: true},
                    {header: 'Arquivo', dataIndex: 'archive', width: 160, sortable: true},
                    {header: 'Função', dataIndex: 'function_name', width: 100, sortable: true},
                    {header: 'Movimentação de Posse', dataIndex: 'possession_unicode', width: 400, sortable: true},
                    {header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, sortable: true, hidden: true},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, sortable: true, hidden: true},
                    {header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true}
                ]
            );

        return this._columnModel;
    },

    defaultValues: function(values) {
        if(values)
            this._defaultValues = values;

        return this._defaultValues;
    },

    createItem: function(values) {
        if(values instanceof Ext.Button)
            values = {};

        values = Ext.applyIf(
            core.nullValue(values, {}),
            this.defaultValues()
        );

        rh.socialsecurity.EmploymentBondGrid.superclass.createItem.call(this, values);
    },

    getFilterMenu: function() {
        return [
            {
                text: 'Tempo',
                menu: [
                    {
                        text: 'Dobrado - FICTO',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleContributionDouble(true); }
                    },
                    {
                        text: 'Normal',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleContributionDouble(false); }
                    }
                ]
            },
            {
                text: 'Previdência Social',
                menu: [
                    {
                        text: 'RGPS',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.togglePensionSystem(1); }
                    },
                    {
                        text: 'RPPS',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.togglePensionSystem(2); }
                    },
                    {
                        text: 'Militar',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.togglePensionSystem(3); }
                    }
                ]
            },
            {
                text: 'Serviço',
                menu: [
                    {
                        text: 'Público',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.togglePublicEmployee(true); }
                    },
                    {
                        text: 'Privado',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.togglePublicEmployee(false); }
                    }
                ]
            },
            {
                text: 'Vínculo',
                menu: [
                    {
                        text: 'PGJ',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleWithPGJ(true); }
                    },
                    {
                        text: 'Externo',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleWithPGJ(false); }
                    }
                ]
            }
        ];
    },

    toggleContributionDouble: function(tipo) {
        if(!this._filterContributionDouble)
            this._filterContributionDouble = [true, false];

        if(this._filterContributionDouble.indexOf(tipo) >= 0)
            this._filterContributionDouble.remove(tipo);
        else
            this._filterContributionDouble.push(tipo);

        this.setFilterProperty('contribution_double__in', this._filterContributionDouble, 1000);
    },

    togglePensionSystem: function(tipo) {
        if(!this._filterPensionSystem)
            this._filterPensionSystem = [1, 2, 3];

        if(this._filterPensionSystem.indexOf(tipo) >= 0)
            this._filterPensionSystem.remove(tipo);
        else
            this._filterPensionSystem.push(tipo);

        this.setFilterProperty('pension_system__in', this._filterPensionSystem, 1001);
    },

    togglePublicEmployee: function(tipo) {
        if(!this._filterPublicEmployee)
            this._filterPublicEmployee = [true, false];

        if(this._filterPublicEmployee.indexOf(tipo) >= 0)
            this._filterPublicEmployee.remove(tipo);
        else
            this._filterPublicEmployee.push(tipo);

        this.setFilterProperty('public_employee__in', this._filterPublicEmployee, 1002);
    },

    toggleWithPGJ: function(tipo) {
        if(!this._filterWithPGJ)
            this._filterWithPGJ = [true, false];

        if(this._filterWithPGJ.indexOf(tipo) >= 0)
            this._filterWithPGJ.remove(tipo);
        else
            this._filterWithPGJ.push(tipo);

        this.setFilterProperty('with_pgj__in', this._filterWithPGJ, 1003);
    },

    cleanFilter: function() {
        try {
            this.setFilterProperty('contribution_double__in', [true, false], 1000, false);
            this.setFilterProperty('pension_system__in', [1, 2, 3], 1001, false);
            this.setFilterProperty('public_employee__in', [true, false], 1002, false);
            this.setFilterProperty('with_pgj__in', [true, false], 1003, false);
        }
        catch(e) { /* não faz nada */ }
    }
});

core.RestfulGrid.register(
    'rh.socialsecurity.EmploymentBondRestful',
    'rh.socialsecurity.EmploymentBondGrid'
);
