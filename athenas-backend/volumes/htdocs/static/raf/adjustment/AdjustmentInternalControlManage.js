
Ext._define('raf.adjustment.AdjustmentInternalControlManage', {
    extend: 'toolkit.widget.TabPanel',

    getAdjustmentGrid: function() {
        if(!this._adjustmentGrid) {
            this._adjustmentGrid = Ext._create('raf.adjustment.AdjustmentInternalControlGrid', {
                title: 'Histórico',
                border: false,
                hideItemsToolbar: ['remove', 'download',],
                columnAction: false,
                gridAutoLoad: false,
                allowRemove: false,
                disabled: true,
                detailView: this.getDisplayTilePanel(),
                configOrderToolBar: ['->','-','undo', '-'],
                doubleClickHandler: function() { },
            });
            // this._adjustmentGrid.setFilterProperty('situation__in', [4, 6], 1000, false);
            this._adjustmentGrid.setFilterProperty('situation__in', [2, 3, 4, 6], 1000, false);

        }
        return this._adjustmentGrid;
    },

    openAnalysisWindow: function() {
        var selected = this.getAdjustmentWaitingGrid().getSelectionModel().getSelected();
        Ext._create('raf.adjustment.AdjustmentAnalysisInternalControlWindow', {
            modal: false,
            params: {
                adjustment: selected.data.pk,
                situation: selected.data.situation,
                gridMain: this._adjustmentWaitingGrid,
            },
        }).show();
    },

    getAdjustmentWaitingGrid: function() {
        if(!this._adjustmentWaitingGrid) {
            this._adjustmentWaitingGrid = Ext._create('raf.adjustment.AdjustmentInternalControlGrid', {
                title: 'Em análise',
                border: false,
                hideItemsToolbar: ['remove', 'download'],
                columnAction: false,
                gridAutoLoad: false,
                allowRemove: false,
                disabled: true,
                colorized: true,
                storeDefaultRoute: 'inbox_waiting',
                detailView: this.getDisplayTilePanel(),
                configOrderToolBar: [],
                doubleClickHandler: function() {
                },
            });
        }
        this._adjustmentWaitingGrid.addListener('dblClick', this.openAnalysisWindow, this);
        return this._adjustmentWaitingGrid;
    },

    getEmployeeGrid: function() {
        if(!this._employeeGrid) {
            this._employeeGrid = Ext._create('raf.EmployeeGrid', {
                region: 'north',
                title: 'Membros',
                height: 300,
                gridAutoLoad: false,
                columnAction: false,
                configOrderToolBar: ['search'],
                hiddenFilter: true,
                storeDefaultRoute: 'employee_adjustment',
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true})
            });
            // this._employeeGrid.setFilterProperty('ativo', true, 2000, false);
            this._employeeGrid.setFilterProperty('tipo', 'M', 2001);
            this._employeeGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
                    if(selection.length > 0)
                        this.employee(selection[0].get('pk'));
                    else
                        this.employee(null);
                }
            });
        }
        return this._employeeGrid;
    },

    getAllEmployeeGrid: function() {
        if(!this._allEmployeeGrid) {
            this._allEmployeeGrid = Ext._create('raf.EmployeeGrid', {
                region: 'north',
                title: 'Todos os Membros',
                height: 300,
                gridAutoLoad: false,
                columnAction: false,
                hideColumns: ['first_adjustment_date'],
                configOrderToolBar: ['search'],
                hiddenFilter: true,
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true})
            });
            this._allEmployeeGrid.setFilterProperty('ativo', true, 2000, false);
            this._allEmployeeGrid.setFilterProperty('tipo', 'M', 2001);
            this._allEmployeeGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
                    if(selection.length > 0)
                        this.employee(selection[0].get('pk'));
                    else
                        this.employee(null);
                }
            });
        }
        return this._allEmployeeGrid;
    },

    getAdjustmentPanel: function() {
        if(!this._personAttendancePanel)
            this._personAttendancePanel = Ext._create('Ext.Panel', {
                region: 'west',
                split: true,
                width: Ext.getBody().getBox().width * 0.55,
                minWidth: Ext.getBody().getBox().width * 0.3,
                maxWidth: Ext.getBody().getBox().width * 0.8,
                border: false,
                layout: 'border',
                items: [
                    {
                        xtype: 'tabpanel',
                        region: 'north',
                        activeTab: 0,
                        items: [
                            this.getEmployeeGrid(),
                            this.getAllEmployeeGrid()
                        ]
                    },
                    {
                        xtype: 'tabpanel',
                        region: 'center',
                        activeTab: 0,
                        items: [
                            this.getAdjustmentWaitingGrid(),
                            this.getAdjustmentGrid()
                        ]
                    }
                ]
            });
        return this._personAttendancePanel;
    },

    getDisplayTilePanel: function() {
        if(!this._displayTilePanel)
            this._displayTilePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
                // disabled: true,
            });

        return this._displayTilePanel;
    },

    employee: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._employee = value;

            if(dispatch) this.observeEmployee();
        }

        return this._employee;
    },

    observeEmployee: function() {
        var value = this.employee();


        if(value) {
            this.getAdjustmentGrid().enable();
            this.getAdjustmentGrid().setFilterProperty('activity__workerlocation__raf__employee', value, 1001);

            this.getAdjustmentWaitingGrid().enable();
            this.getAdjustmentWaitingGrid().setFilterProperty('activity__workerlocation__raf__employee', value, 1001);

        } else {
            this.getAdjustmentGrid().disable();
            this.getAdjustmentGrid().removeFilterProperty('activity__workerlocation__raf__employee', 1001, false);
            this.getAdjustmentGrid().getStore().removeAll();

            this.getAdjustmentWaitingGrid().disable();
            this.getAdjustmentWaitingGrid().removeFilterProperty('activity__workerlocation__raf__employee', 1001, false);
            this.getAdjustmentWaitingGrid().getStore().removeAll();
        }

    },

    adjustment: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._adjustment = value;

            if(dispatch) this.observeAdjustment();
        }

        return this._adjustment;
    },

    observeAdjustment: function() {
        var value = this.adjustment();

        if(value) {

            var rest = value.grid.factoryRestful();
            var mask = new Ext.LoadMask(this.getDisplayTilePanel().getEl(), {msg: 'buscando documento...'});

            mask.show();
            rest.rendererDocument(
                value.pk,
                {
                    scope: this,
                    fn: function(document) {

                        this.getDisplayTilePanel().enable();
                        this.getDisplayTilePanel().setPageContent(document.content);
                    }
                },
                {
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Buscando documento',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {fn: function() {mask.hide();}}
            );
        }
        else {
            this.getDisplayTilePanel().disable();
            this.getDisplayTilePanel().setPageContent('');
        }

    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Ajustes de atividade'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getAdjustmentPanel(),
                    this.getDisplayTilePanel()
                ]
            }
        );

        raf.adjustment.AdjustmentInternalControlManage.superclass.constructor.call(this, cfg);

        this.observeEmployee();
        this.observeAdjustment();
    }
});
