Ext._define('corregedoria.cirdir.health.healtharea.Manage', {
  extend: 'toolkit.widget.TabPanel',

    getGrid: function(cfg) {
        if(!this._grid) {
            this._grid = Ext._create('corregedoria.cirdir.Grid', {
                region: 'center',
                gridAutoLoad: false,
                rest: 'corregedoria.cirdir.health.healtharea.Restful',
                height: Ext.getBody().getBox().height * 0.90,
                width: Ext.getBody().getBox().width * 0.55,
                detailView: this.getTilePanel(),
                configOrderToolBar: ['menuHealthArea', 'applyFilterHealthArea', 'reportsHealthArea', '->', '-', 'search'],
                hideColumns: ['icons'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                params: {
                  admin: false,
                  health_area: true,
                }
            });
            this._grid.setParam('mainGrid', this._grid);
            this._grid.getStore().on({
                scope: this,
                load: function(sel) {
                  var selection = this._grid.getSelectionModel().getSelections();
                  if(selection.length == 1){
                      this.observerCIRDIR(selection[0].get('pk'));
                  } else {
                    this.observerCIRDIR();
                    this._grid.getSelectionModel().clearSelections();
                  }
                },
            });
            this._grid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();
                    if(selection.length == 1){
                        this.observerCIRDIR(selection[0].get('pk'));
                    }
                }
            });
        }
        return this._grid;
    },

    getBoxPanel: function(cfg) {
        if(!this._boxPanel)
            this._boxPanel = Ext._create('Ext.Panel', {
                region: 'center',
                split: true,
                border: false,
                autoHeight: true,
                items: [
                    this.getGrid(cfg),
                ]
            });
        return this._boxPanel;
    },

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                region: 'east',
                split: true,
                width: Ext.getBody().getBox().width * 0.45,
                minWidth: Ext.getBody().getBox().width * 0.2,
                maxWidth: Ext.getBody().getBox().width * 0.8
            });
        return this._tilePanel;
    },

    controlinformation: function(value, dispatch) {
        this._controlinformation = value;
        return this._controlinformation;
    },

    observerCIRDIR: function(value) {
        if(value) {
            this.readView(value);
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },

    readView: function(controlinformation) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        // var rest = Ext._create('corregedoria.cirdir.EmployeeRestful');
        var rest = this.getGrid().factoryRestful();
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document_health_area'),
            scope: this,
            autoAbort: true,
            params: {
                controlinformation: controlinformation
            },
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var me = this;
                if(rst.success) {
                    this.getTilePanel().setPageContent(rst.content);
                }
                else
                    Ext.Msg.show({
                        title: 'Carregando informações',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Carregando informações',
                    msg: 'Recurso indisponivel no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    employee: function(cfg, value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._employee = value;
            if(dispatch) this.observerEmployee(cfg);
        }
        return this._employee;
    },

    observerEmployee: function(cfg) {
        // var value = this.employee(cfg);
        var value = this._employee;
        if (this.admin == true) {
            this.getGrid(cfg).getReportsHealthAreaAction().show();
            this.getGrid(cfg).getApplyFilterHealthAreaAction().show();
            this.getGrid(cfg).getMenuHealthAreaAction().show();
            this.getGrid(cfg).getStore().load();
        } else {
            this.getGrid(cfg).getStore().load();
            // this.getGrid(cfg).setFilterProperty('employee', value);
        }
    },

    autoSelectionEmployee: function(cfg) {
        if(this.employee(cfg) === undefined) {
            var rest = Ext._create('corregedoria.cirdir.EmployeeRestful');
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Selecionando usuário...'});
            mask.show();
            rest.doRequest(
                rest.getRoute('employee_initial', false, 'POST', {
                    params: {
                        health_area: 'true',
                    },
                    scope: this,
                    callback: function() {
                        mask.hide();
                        mask = null;
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);
                        if(rst.success) {
                            this.admin = rst.data.admin;
                            this.employee(cfg, rst.data.pk);
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
        cfg = cfg ? cfg : {};
        Ext.applyIf(
            cfg,
            {
                title: 'Você é Único'
            }
        );
        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getBoxPanel(cfg),
                    this.getTilePanel(cfg)
                ],
            }
        );
        corregedoria.cirdir.health.healtharea.Manage.superclass.constructor.call(this, cfg);
        this.autoSelectionEmployee(cfg);
        this.observerCIRDIR();
    },
});
