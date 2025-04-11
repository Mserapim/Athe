/**
 *
 **/
 Ext._define('rh.employee.workplace.workassignmentsubstitution.ManagePanel', {
    extend: 'Ext.Panel',

    getWorkassignmentSubstitutedGrid: function(cfg_window, cfg) {
        if(!this._workassignmentSubstitutedGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Exercícios do servidor afastado',
                    region: 'north',
                    split: true,
                    minHeight: 450,
                    height: 300,
                    columnAction: false,
                    gridAutoLoad: false,
                    hideItemsToolbar: ['add', 'edit', 'remove'],
                    border: false,
                }
            );
            this._workassignmentSubstitutedGrid = Ext._create('rh.employee.workplace.workassignmentsubstitution.Grid', cfg);
            this._workassignmentSubstitutedGrid.setParam('designacao', true);
            this._workassignmentSubstitutedGrid.setFilterProperty('designacao', true, 1, false);
            if(cfg.employee_registry != undefined)
                this._workassignmentSubstitutedGrid.setFilterProperty('servidor__matricula', cfg.employee_registry, 7, false);
            if(cfg.employee_pk != undefined)
                this._workassignmentSubstitutedGrid.setParam('servidor', cfg.employee_pk);

            this._workassignmentSubstitutedGrid.getStore().reload();

            this._workassignmentSubstitutedGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.employeeWorkplace(record.get('pk'));
                    this.workplace(record.get('lotacao'));
                },
                rowdeselect: function(sm) {
                    this.employeeWorkplace(null);
                    this.workplace(null);
                }
            });

            this._workassignmentSubstitutedGrid.getStore().on({
                scope: this,
                load: function() {
                    this.employeeWorkplace(null);
                    this.workplace(null);
                }
            });

            this._workassignmentSubstitutedGrid.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._workassignmentSubstitutedGrid.getSelectionModel().getSelected());

                    if(selected){
                        this.employeeWorkplace(selected.get('pk'));
                        this.workplace(selected.get('lotacao'));
                    }
                    else{
                        this.employeeWorkplace(null);
                        this.workplace(null);
                    }
                }
            });
        }
        return this._workassignmentSubstitutedGrid;
    },

    workplace: function(value, prevent) {
        prevent = core.nullValue(prevent, false);
        if(value !== undefined) {
            this._workplace = value;
            !prevent && this.observeWorkplace();
        }
        return this._workplace;
    },

    employeeWorkplace: function(value, prevent) {
        prevent = core.nullValue(prevent, false);
        if(value !== undefined) {
            this._employeeWorkplace = value;
        }
        return this._employeeWorkplace;
    },

    observeWorkplace: function() {
        var value = this.workplace();
        var grid;

        if(value) {
            this.getWorkassignmentGeneralGrid().setParam('lotacao', value);
            this.getWorkassignmentGeneralGrid().setFilterProperty('lotacao', value, 6, false);
            this.getWorkassignmentGeneralGrid().setFilterProperty('pk', this.employeeWorkplace(), -1);
            this.getWorkassignmentGeneralGrid().setDisabled(false);
        }
        else {
            this.getWorkassignmentGeneralGrid().setParam('lotacao', 0);
            this.getWorkassignmentGeneralGrid().setFilterProperty('lotacao', 0, 6, false);
            this.getWorkassignmentGeneralGrid().setFilterProperty('pk', 0, -1, false);
            this.getWorkassignmentGeneralGrid().setDisabled(true);
        }
    },

    getWorkassignmentGeneralGrid: function(cfg_window, cfg) {
        if(!this._workassignmentGeneralGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Exercícios do local selecionado acima',
                    region: 'center',
                    gridAutoLoad: false,
                    minHeight: 300,
                    columnAction: false,
                    gridAutoLoad: false,
                    border: false,
                    disabled: true,
                }
            );
            this._workassignmentGeneralGrid = Ext._create('rh.employee.workplace.workassignmentsubstitution.Grid', cfg);
            this._workassignmentGeneralGrid.setParam('designacao', true);
            this._workassignmentGeneralGrid.setFilterProperty('designacao', true, 1, false);
        }
        return this._workassignmentGeneralGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getWorkassignmentSubstitutedGrid(cfg, {
                        departure: cfg.departure,
                        departament: cfg.departament,
                        employee_registry: cfg.employee_registry,
                        employee_pk: cfg.employee_pk,
                    }),
                    this.getWorkassignmentGeneralGrid(cfg, {departament: cfg.departament}),
                ]
            }
        );
        rh.employee.workplace.workassignmentsubstitution.ManagePanel.superclass.constructor.call(this, cfg);
    }
});