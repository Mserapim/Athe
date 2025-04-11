Ext._define('raf.functionalactivityreport.Launcher', {
    extend: 'toolkit.widget.TabPanel',

    getFunctionalActivityReportGroupGrid: function() {
        var management = 0;
        if(this.param !== undefined) {
            management = this.param.management_enable;
        }
        if(!this._functionalActivityReportGroupGrid) {
            this._functionalActivityReportGroupGrid = Ext._create('raf.functionalactivityreport.GroupGrid', {
                region: 'west',
                title: 'RAFs',
                width: 450,
                maxWidth: 450,
                minWidth: 250,
                split: true,
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                hideHeaders: true,
                management_enable: management
            });
            this._functionalActivityReportGroupGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
                    if(selection.length > 0)
                        this.functionalActivityReport(selection[0]);
                    else
                        this.functionalActivityReport(null);
                }
            });
        }
        return this._functionalActivityReportGroupGrid;
    },

    locationsFollow: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._locationsFollow = value;
            if(dispatch) this.observerLocationsFollow();
        }
        return this._locationsFollow;
    },

    observerLocationsFollow: function() {
        var value = this.locationsFollow();

        if(value) {
            this.getFunctionalActivityReportGroupGrid().setLocationsFollow(value, false);
        }
        else {
            this.getFunctionalActivityReportGroupGrid().setLocationsFollow(value, false);
        }
    },

    employee: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._employee = value;
            if(dispatch) this.observerEmployee();
        }
        return this._employee;
    },

    observerEmployee: function() {
        var value = this.employee();
        if(value) {
            this.getFunctionalActivityReportGroupGrid().setValueEmployee(value);
        }
        else {
            this.getFunctionalActivityReportGroupGrid().setValueEmployee(0);
        }
    },

    functionalActivityReport: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._functionalActivityReport = value;
            if(dispatch)
                this.observeFunctionalActivityReport();
        }
        return this._functionalActivityReport;
    },

    observeFunctionalActivityReport: function() {
        var value = this.functionalActivityReport();
        if(value) {
            this.getWorkerLocationGrid().enable();
            this.getWorkerLocationGrid().setParam('raf', value.get('pk'));
            this.getWorkerLocationGrid().setFilterProperty('raf', value.get('pk'), 0);
        } else  {
            this.getWorkerLocationGrid().disable();
            this.getWorkerLocationGrid().setParam('raf', 0);
            this.getWorkerLocationGrid().setFilterProperty('raf', value, 0, false);
            this.getWorkerLocationGrid().getStore().removeAll();
        }
    },

    getWorkerLocationGrid: function() {
        if (!this._workerLocationGrid) {
            this._workerLocationGrid = Ext._create('raf.workerlocation.Grid', {
                region: 'north',
                title: 'Órgãos de Execução',
                margins: '0 0 1 0',
                split: true,
                height: 300,
                minHeight: 250,
                maxHeight: 650,
                gridAutoLoad: false,
                columnAction: false,
                configOrderToolBar: ['search'],
                hideColumns: ['raf_unicode'],
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
            });
            this._workerLocationGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
                    if(selection.length > 0)
                        this.workerLocation(selection[0]);
                    else
                        this.workerLocation(null);
                }
            });
        }
        return this._workerLocationGrid;
    },

    workerLocation: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._workerLocation = value;
            if(dispatch)
                this.observeWorkerLocation();
        }
        return this._workerLocation;
    },

    observeWorkerLocation: function() {
        var value = this.workerLocation();
        if(value) {
            this.getQuizzesGrid().enable();
            this.getQuizzesGrid().setFilterProperty('yearbase__functionalactivityreports', value.get('raf'), 0, true);
        } else  {
            this.getQuizzesGrid().disable();
            this.getQuizzesGrid().getStore().removeAll();
        }
    },

    fillActivities: function() {
        Ext._create('raf.FillActivity.Window', {
            modal: true,
            values: {
                'workerlocation_obj': this.workerLocation(),
                'quiz_obj': this.getQuizzesGrid().getSelectionModel().getSelected()
            },
        }).show();
    },

    getQuizzesGrid: function() {
        if (!this._quizzesGrid) {
            var self = this;
            this._quizzesGrid = Ext._create('raf.quiz.Grid', {
                region: 'center',
                flex: 1,
                layout: 'fit',
                title: 'Questionários',
                margins: '1 0 0 0',
                columnAction: false,
                gridAutoLoad: false,
                hideColumns: ['icons','yearbase_unicode', 'actions'],
                hideItemsToolbar: ['add', 'edit', 'copy', 'remove', '-', 'search', 'download'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                hiddenFilter: true,
                doubleClickHandler: function() {
                    self.fillActivities();
                }
            });
            this.getQuizzesGrid().getStore().removeAll();
        }
        return this._quizzesGrid;
    },

    openChangeWindow: function() {
        Ext._create('raf.functionalactivityreport.ChangeEmployeeWindow', {
            modal: true,
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        this.employeeSelected(instance);
                    }
                }
            }
        }).show();
    },

    employeeSelected: function(instance) {
        console.log(instance)
        if(instance) {
            this.getChangeEmployeeAction().setText(instance.data.pessoa_fisica_unicode);
            this.employee(instance.data.pk);
            this.locationsFollow(instance.data.locations_follow);
        } else if(!this.employee()){
            this.getChangeEmployeeAction().setText(this.defaultText());
            this.employee(null);
            this.locationsFollow([])
        }
    },

    defaultText: function() {
        return "Clique aqui para selecionar um Membro";
    },

    getChangeEmployeeAction: function() {
        if(!this._changeEmployeeAction){
            this._changeEmployeeAction = new Ext.Button({
                xtype: 'button',
                text: this.defaultText(),
                iconCls: 'icon-core icon-core-set-employee',
                scope: this,
                handler: function() {
                    this.openChangeWindow();
                }
            });
        }
        return this._changeEmployeeAction;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = Ext._create('Ext.Toolbar', {
                buttonAlign:'center',
                items: [
                    this.getChangeEmployeeAction()
                ]
            });
        }
        return this._toolbar;
    },

    autoSelectionEmployee: function() {
        if(this.employee() === undefined) {
            var rest = Ext._create('raf.EmployeeRestful');
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Selecionando usuário...'});
            mask.show();
            rest.doRequest(
                rest.getRoute('employee_initial', false, 'GET', {
                    scope: this,
                    callback: function() {
                        mask.hide();
                        mask = null;
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);
                        if(rst.success) {
                            this.employeeSelected(rst);
                        }
                        else
                            Ext.Msg.show({
                                title: 'Selecionando usuário',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    },
                    failure: function(xhr) {
                        Ext.Msg.show({
                            title: 'Selecionando usuário',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Nao foi possível realizar essa operação.'
                        });
                    }
                })
            );
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        this.param = cfg.values;
        Ext.applyIf(
            cfg,
            {
                title: 'Gestor Principal'
            }
        );
        Ext.apply(
            cfg,
            {
                layout: 'border',
                tbar: this.getToolbar(),
                items: [
                    this.getFunctionalActivityReportGroupGrid(),
                    {
                        region: 'center',
                        layout: 'border',
                        border: false,
                        items: [
                            this.getWorkerLocationGrid(),
                            this.getQuizzesGrid(),
                        ]
                    }
                ]
            }
        );
        raf.functionalactivityreport.Launcher.superclass.constructor.call(this, cfg);
        this.functionalActivityReport(cfg.oId === undefined ? null : cfg.oId);
        this.workerLocation(cfg.oId === undefined ? null : cfg.oId);
        this.autoSelectionEmployee();
    },
});
