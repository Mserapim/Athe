
Ext._define('rh.afastamento.ManagerTab', {
    extend: 'Ext.Panel',

    getGrid: function(args) {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.ManagerGrid', {
                title: 'Afastamentos',
                department: args.department,
                region: 'north',
                split: true,
                minHeight: 200,
                height: 250,
            });

            this._grid.getSelectionModel().on({
                scope: this,
                rowselect: function (sm, index, record) {
                    this.employee(record.data['servidor']);
                    this.absence(record.get('pk'));
                },
                rowdeselect: function (sm) {
                    this.employee(null);
                }
            });

            this._grid.getStore().on({
                scope: this,
                load: function () {
                    this.employee(null);
                }
            });

            this._grid.getStore().on({
                scope: this,
                load: function () {
                    var selected = (this._grid.getSelectionModel().getSelected());

                    if (selected){
                        this.employee(selected.get('pk'));
                        this.absence(selected.get('pk'));
                    }else
                        this.employee(null);
                }
            });
        }
        
        return this._grid;
    },

    getWorkassignmentGrid: function (cfg_window, cfg, gridClass) {
        if (!this._workassignmentGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Designações de Exercício',
                    region: 'east',
                    split: true,
                    width: "50%",
                    columnAction: false,
                    disabled: true,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'setMain'],
                    doubleClickHandler: function() {},
                }
            );

            gridClass = gridClass == undefined ? 'rh.afastamento.workassignment.WorkassignmentGrid' : gridClass;
            this._workassignmentGrid = Ext._create(gridClass, cfg);

            this._workassignmentGrid.setParam('designacao', true);
            this._workassignmentGrid.setFilterProperty('designacao', true, 1, false);
        }
        return this._workassignmentGrid;
    },


    getControlPanel: function () {
        if (!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                width: 15,
                frame: true,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0
                },
            });
        return this._controlPanel;
    },

    employee: function (value, prevent) {
        prevent = core.nullValue(prevent, false);

        if (value !== undefined) {
            this._employee = value;

            this._workplace = undefined;
            this._possession = undefined;

            !prevent && this.observeEmployee();
        }

        return this._employee;
    },


    absence: function (value, prevent) {
        prevent = core.nullValue(prevent, false);
        if (value !== undefined) {
            this._absence = value;

            !prevent && this.observeAbsence();
        }

        return this._absence;
    },


    observeAbsence: function(){
        var value = this._absence;
        if (value != undefined) {
            this.getMovimentationSubstitutionsGrid().enable();
            
            this.getMovimentationSubstitutionsGrid().setFilterProperty('afastamento', 0, 200, false);
            this.getMovimentationSubstitutionsGrid().setFilterProperty('movimentacaosubstituicaomembro__afastamento', 0, 200, true);

            this.getMovimentationSubstitutionsGrid().setParam('afastamento', value);
            this.getMovimentationSubstitutionsGrid().setFilterProperty('afastamento', value, 200, false);
            this.getMovimentationSubstitutionsGrid().setFilterProperty('movimentacaosubstituicaomembro__afastamento', value, 200, true);
        }     
    },

    observeEmployee: function () {
        var value = this.employee();
        if (value != undefined) {
            this.getWorkassignmentGrid().enable();
            this.getWorkassignmentGrid().setParam('servidor', value);
            this.getWorkassignmentGrid().setFilterProperty('servidor__pk', value, 200);
        }
    },

    employeeWorkplace: function (record, prevent) {
        prevent = core.nullValue(prevent, false);
        if (record != undefined && record.get('pk') !== undefined) {
            this._employeeWorkplace = record.get('pk');
            this._workplace = record.get('lotacao');
            this._possession = record.get('movimentacao_posse');

            !prevent && this.observeWorkplace();
        }

        return this._employeeWorkplace;
    },

    observeWorkplace: function () {
        if (this._employeeWorkplace != undefined) {
            this.getWorkassignmentGrid().setParam('child_of', this._employeeWorkplace);
            this.getWorkassignmentGrid().setParam('lotacao', this._workplace);
            this.getWorkassignmentGrid().setParam('movimentacao_posse', this._possession);
            this.getWorkassignmentGrid().setFilterProperty('child_of', this._employeeWorkplace, 300);
        }
        else {
            this.getWorkassignmentGrid().setParam('child_of', undefined);
            this.getWorkassignmentGrid().setParam('lotacao', undefined);
            this.getWorkassignmentGrid().setParam('movimentacao_posse', undefined);
            if (this.getWorkassignmentGrid().getParams().child_of != undefined) {
                this.getWorkassignmentGrid().removeFilterProperty('child_of');
                this.getWorkassignmentGrid().getStore().reload();
            }
        }
    },

    // getPendingExercisesGrid: function(args) {
    //     if(!this._pendingExercisesGrid)
    //         this._pendingExercisesGrid = Ext._create('rh.employee.workplace.managerbyworkplace.pendingexercises.ManagePanel', {
    //             title: 'Órgãos com exercícios pendentes',
    //             department: args.department,
    //             region: 'center',
    //         });
    //     return this._pendingExercisesGrid;
    // },

    // getPendingExercisesMemberGrid: function(args) {
    //     if(!this._memberPendingExercisesGrid)
    //         this._memberPendingExercisesGrid = Ext._create('rh.employee.workplace.managerbyemployee.pendingexercises.ManagePanel', {
    //             title: 'Membros com exercícios pendentes',
    //             department: args.department,
    //             region: 'center',
    //         });
    //     return this._memberPendingExercisesGrid;
    // },

    // getExercisesMoreThanOneGrid: function(args) {
    //     if(!this._exercisesMoreThanOneGrid)
    //         this._exercisesMoreThanOneGrid = Ext._create('rh.employee.workplace.exercisesmorethanone.ManagerPanel', {
    //             title: 'Locais com mais de 1 exercício',
    //             department: args.department,
    //             region: 'center',
    //         });
    //     return this._exercisesMoreThanOneGrid;
    // },


    employeeWorkplace: function (record, prevent) {
        prevent = core.nullValue(prevent, false);
        if (record != undefined && record.get('pk') !== undefined) {
            this._employeeWorkplace = record.get('pk');
            this._workplace = record.get('lotacao');
            this._possession = record.get('movimentacao_posse');

            !prevent && this.observeWorkplace();
        }

        return this._employeeWorkplace;
    },

    getMovimentationSubstitutionsGrid: function (cfg_window, cfg, gridClass) {
        if (!this._movimentationSubstitutionsGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Substituições',
                    region: 'center',
                    columnAction: false,
                    disabled: true,
                }
            );

            gridClass = gridClass == undefined ? 'rh.movimentacao.substituicao.DepartureGrid' : gridClass;
            this._movimentationSubstitutionsGrid = Ext._create(gridClass, cfg);
            
            this._movimentationSubstitutionsGrid.setFilterProperty('afastamento', 0, 200);
            this._movimentationSubstitutionsGrid.setFilterProperty('movimentacaosubstituicaomembro__afastamento', 0, 200);
            this._movimentationSubstitutionsGrid.setSortProperty('data_inicio', 'DESC');
        }
        return this._movimentationSubstitutionsGrid;
    },
    

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};
        Ext.apply(
            cfg,
            {
                region: 'center',
                layout: 'border',
                border: false,
                scope: this,
                items: [
                    this.getGrid({
                        department: cfg.department
                    }),
                    {
                        region: 'center',
                        layout: 'border',
                        minHeight: 150,
                        scope: this,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getMovimentationSubstitutionsGrid(cfg),
                            this.getControlPanel(),
                            this.getWorkassignmentGrid(cfg)
                        ]
                        
                    }
                ],
                listeners: {
                    scope: this,
                    afterrender: function (owner) {
                        var grid = owner.getWorkassignmentGrid();
                        setTimeout(function () {
                            grid.enable();
                            grid.disable();
                        }, 100);
                    }
                }
            }
        );

        rh.afastamento.ManagerTab.superclass.constructor.call(this, cfg);

        var grid = this.getWorkassignmentGrid();
        setTimeout(function () {
            grid.enable();
            grid.disable();
        }, 100);
    }
});
