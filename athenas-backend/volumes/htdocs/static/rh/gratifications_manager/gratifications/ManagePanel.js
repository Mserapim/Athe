Ext._define('rh.gratifications_manager.gratifications.ManagePanel', {
    extend: 'Ext.Panel',

    rangeYear: function(thisYear){
        var years = [];
        for (let i = 2004; i <= thisYear +1; i++) {
            item  = [i, i.toString()]
            years.push(item);
        }

        return years;
    },

    getEmployeeGrid: function (cfg_window, cfg) {
        if (!this._employeeGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Servidores',
                    grid_name: 'rh.gratifications_manager.gratifications.EmployeeGrid',
                    rest: 'rh.employee.Restful',
                    region: 'north',
                    split: true,
                    minHeight: 200,
                    height: 250,
                    hideActions: ['edit', 'remove', 'copy'],
                    hideItemsToolbar: ['add', 'edit', 'remove'],                
                    doubleClickHandler: function () { }
                },
            );
            this._employeeGrid = Ext._create(cfg.grid_name, cfg);
            this._employeeGrid.setFilterProperty(
                'type_by_possession__in',
                ['MBR', 'MEL', 'MCM', 'MEC', 'MBR2', 'MEL2', 'MCM2', 'MEC2', 'MAP', 'MAP2'],
                1,
                false
            );
            this._employeeGrid.setFilterProperty('ativo', true, 2, true);
            
            this._employeeGrid.getSelectionModel().on({
                scope: this,
                rowselect: function (sm, index, record) {
                    this.employee(record.get('pk'));
                },
                rowdeselect: function (sm) {
                    this.employee(null);
                }
            });

            this._employeeGrid.getStore().on({
                scope: this,
                load: function () {
                    this.employee(null);
                }
            });

            this._employeeGrid.getStore().on({
                scope: this,
                load: function () {
                    var selected = (this._employeeGrid.getSelectionModel().getSelected());

                    if (selected)
                        this.employee(selected.get('pk'));
                    else
                        this.employee(null);
                }
            });
            
            this._employeeGrid._toolbar.insert(
                3,
                '-',
                    {
                        xtype: 'combo',
                        store: new Ext.data.JsonStore({
                            proxy: new Ext.data.HttpProxy({
                                url: toolkit.util.Normalize.controller_action('GFPControlador', 'anos_folha'),
                                disableCaching: true,
                                method: 'GET'
                            }),
                            root: 'root',
                            fields: ['pk', 'description']
                        }),
                        displayField: 'description',
                        valueFeild: 'pk',
                        emptyText: 'Ano para filtro',
                        width: 140,
                        triggerAction: 'all',
                        value: this._today.getFullYear(),
                        listeners: {
                            scope: this,
                            select: function (combo, record) {
                                var store = this.getEmployeeWorkplaceGrid().getStore();
                                var wstore = this.getWorkassignmentGrid().getStore();

                                if (record.get('pk') != 0)
                                    this._year = record.get('pk')
                                else
                                    this._year = null
                                    
                                this.observeEmployee()
                                store.load({});
                                wstore.load({});
                            }
                        }
                    },
                    '-',
                    {
                        xtype: 'combo',
                        store: [
                            [1, 'JANEIRO'],
                            [2, 'FEVEREIRO'],
                            [3, 'MARÇO'],
                            [4, 'ABRIL'],
                            [5, 'MAIO'],
                            [6, 'JUNHO'],
                            [7, 'JULHO'],
                            [8, 'AGOSTO'],
                            [9, 'SETEMBRO'],
                            [10, 'OUTUBRO'],
                            [11, 'NOVEMBRO'],
                            [12, 'DEZEMBRO'],
                        ],
                        emptyText: 'Mês para filtro',
                        width: 140,
                        triggerAction: 'all',
                        value: this._today.getMonth() + 1,
                        listeners: {
                            scope: this,
                            select: function (combo, record) {
                                var store = this.getEmployeeWorkplaceGrid().getStore();
                                var wstore = this.getWorkassignmentGrid().getStore();

                                if (record.get('field1') != 0)
                                    this._month = record.get('field1');
                                    
                                else
                                    this._month = null
                                    
                                this.observeEmployee()
                                store.load({});
                                wstore.load({});
                            }
                        }
                    },
                    '-',
                        
            );
        }
        

        return this._employeeGrid;
    },

   

    employee: function (value, prevent) {
        prevent = core.nullValue(prevent, false);

        if (value !== undefined) {
            this._employee = value;

            this._workplace = undefined;
            this._possession = undefined;

            !prevent && this.observeEmployee();

            !prevent && this.observeWorkplace(); 
        }

        return this._employee;
    },

    observeEmployee: function () {
        var value = this.employee();
        if (value != undefined) {
            this.getWorkassignmentGrid().enable();
            this.getWorkassignmentGrid().setParam('servidor', value);            
            this.getEmployeeWorkplaceGrid().setParam('servidor', value);

            if (this._month && this._year){
                this.getEmployeeWorkplaceGrid().setParam('year', this._year);
                this.getEmployeeWorkplaceGrid().setParam('month', this._month);
                
                const date = new Date(this._year, this._month).toISOString().substring(0, 10);
                var d_end = new Date(this._year, this._month+1)

                d_end.setDate(d_end.getDate() - 1);
                d_end = d_end.toISOString().substring(0, 10)

                this.getWorkassignmentGrid().setFilterProperty('servidor__pk', value, 200, false);
                this.getWorkassignmentGrid().setFilterProperty('data_vigencia_inicio__lte', d_end, 2, false);
                this.getWorkassignmentGrid().setFilterProperty('data_vigencia_fim__gte', date, 3, false);
                this.getWorkassignmentGrid().setFilterProperty('data_vigencia_fim__isnull', true, 3, true);
            } else {
                this.getWorkassignmentGrid().setFilterProperty('servidor__pk', value, 200, true);
            }
        } else {
            var employee = this.getEmployeeWorkplaceGrid().getParams().servidor;
            if (employee != undefined) {
                this.getEmployeeWorkplaceGrid().disable();
                this.getEmployeeWorkplaceGrid().getStore().removeAll();

                this.getWorkassignmentGrid().disable();
                this.getWorkassignmentGrid().setParam('servidor', 0);
                this.getWorkassignmentGrid().setParam('child_of', undefined);
                this.getWorkassignmentGrid().setParam('lotacao', undefined);
                this.getWorkassignmentGrid().setParam('movimentacao_posse', undefined);
                this.getWorkassignmentGrid().setFilterProperty('servidor__pk', 0, 200, false);
                this.getWorkassignmentGrid().removeFilterProperty('child_of', 300, false);
            }
        }
    },

    employeeWorkplace: function (workplaces, prevent) {
        if (workplaces != undefined){
            this._workplaces = workplaces;
        }
            !prevent && this.observeWorkplace();
        return this._workplaces;
    },

    observeWorkplace: function () {
        if (this._workplaces != undefined) {
            var value = this.employee();

            this.getEmployeeWorkplaceGrid().enable();
            this.getEmployeeWorkplaceGrid().getStore().baseParams['year'] =this._year
            this.getEmployeeWorkplaceGrid().getStore().baseParams['month'] =this._month
            this.getEmployeeWorkplaceGrid().getStore().baseParams['employee'] = value
            this.getEmployeeWorkplaceGrid().getStore().baseParams['workplaces'] = this._workplaces
            this.getEmployeeWorkplaceGrid().setParam('workplace__in', this._workplaces);
            this.getEmployeeWorkplaceGrid().setFilterProperty('workplace__in', this._workplaces, 100);
        } else {
            this.getEmployeeWorkplaceGrid().disable();
            this.getEmployeeWorkplaceGrid().setParam('workplace__in', []);
            this.getEmployeeWorkplaceGrid().setFilterProperty('workplace__in', [], 100, false);
            this.getEmployeeWorkplaceGrid().getStore().removeAll();
        }
    },

    getEmployeeWorkplaceGrid: function (cfg_window, cfg, gridClass) {
        if (!this._employeeWorkplaceGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Gratificações',
                    flex: 1.0,
                    border: false,
                }
            );

            gridClass = gridClass == undefined ? 'rh.gratifications_manager.gratifications.workplace_tag.Grid' : gridClass;
            this._employeeWorkplaceGrid = Ext._create(gridClass, cfg);

        }
        return this._employeeWorkplaceGrid;
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

    getWorkassignmentGrid: function (cfg_window, cfg, gridClass) {
        if (!this._workassignmentGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Designações de Exercício',
                    flex: 1.0,
                    border: false,
                    columnAction: false,
                    disabled: true,
                    hideItemsToolbar: ['add', 'edit', 'remove'],
                }
            );

            gridClass = gridClass == undefined ? 'rh.gratifications_manager.gratifications.workassignment.Grid' : gridClass;
            this._workassignmentGrid = Ext._create(gridClass, cfg);

            this._workassignmentGrid.setParam('designacao', true);
            this._workassignmentGrid.setFilterProperty('designacao', true, 1, false);
            
            this._workassignmentGrid.getSelectionModel().on({
                scope: this,
                rowselect: function (sm, index, record) {

                },
                rowdeselect: function (sm) {
                }
            });


            this._workassignmentGrid.getStore().on({
                scope: this,
                load: function () {
                    var store = this._workassignmentGrid.store
                    if (store.data.items){
                        var _workplaces = []
                        store.data.items.forEach(function(item){
                            _workplaces.push(item.data.lotacao)
        
                        })
                    };
        
                    if (_workplaces) {
                        this.employeeWorkplace(_workplaces);
                    } else {
                        this.employeeWorkplace(null);
                    }
                    
                }
            });

        }
        return this._workassignmentGrid;
    },

    firstCall: function () {
        this.observeEmployee();
        this.observeWorkplace();
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        const timeElapsed = Date.now();
        this._today = new Date(timeElapsed);
        this._year = this._today.getFullYear();
        this._month = this._today.getMonth() + 1;

        Ext.applyIf(
            cfg,
            {
                region: 'center',
                layout: 'border',
                border: false,
                scope: this,
                items: [
                    this.getEmployeeGrid(cfg, { departament: cfg.departament }),
                    {
                        region: 'center',
                        layout: 'hbox',
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
                            this.getWorkassignmentGrid(cfg),
                            
                            this.getControlPanel(),

                            this.getEmployeeWorkplaceGrid(cfg)
                            
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
        rh.gratifications_manager.gratifications.ManagePanel.superclass.constructor.call(this, cfg);
        this.firstCall();

        var grid = this.getWorkassignmentGrid();
        setTimeout(function () {
            grid.enable();
            grid.disable();
        }, 100);

    }
});
