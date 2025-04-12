Ext._define('corregedoria.cirdir.health.healtharea.attendance.Manage', {
  extend: 'toolkit.widget.TabPanel',


    getGrid: function(cfg) {
        if(!this._grid) {
            this._grid = Ext._create('corregedoria.cirdir.health.healtharea.attendance.Grid', {
                title: 'Questionários - Vc é Único',
                border: true,
                height: Ext.getBody().getBox().height * 0.30,
                width: Ext.getBody().getBox().width * 0.55,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                doubleClickHandler: function() { },
                gridAutoLoad: false,
                columnAction: false,
                hiddenFilter: true,
            });

            this._grid.addFilterProperty('evaluated', false, 2001, false);

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
            this._boxPanel = Ext._create('Ext.form.FormPanel', {
                region: 'center',
                split: true,
                border: false,
                autoHeight: true,
                items: [
                    this.getGrid(cfg),
                    {
                        xtype: 'panel',
                        title: 'Avaliação',
                        id: 'formeditor',
                        layout: 'form',
                        items: [
                            {
                                xtype: 'ckeditor',
                                id: 'editor',
                                hideLabel: true,
                                allowBlank: false,
                                name: 'message',
                                height: Ext.getBody().getBox().height * 0.45,
                                submit: true,
                                toolbarGroups: [
                                    {name: 'styles', itens: ['Format']},
                                    {name: 'clipboard'},
                                    {name: 'editing'},
                                    {name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ]},
                                    {
                                        name: 'paragraph',
                                        groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                                    },
                                ],
                            },
                        ],
                        buttons: [
                            {
                                text: 'Salvar',
                                id: 'btnsalvar',
                                scope: this,
                                handler: function() {
                                    Ext.Msg.show({
                                        title: 'teste...',
                                        msg: 'teste',
                                        icon: Ext.Msg.INFO,
                                        buttons: Ext.Msg.OK
                                    });
                                },
                            },
                            {
                                text: '<b>Salvar e Enviar</b>',
                                id: 'btnsalvareenviar',
                                scope: this,
                                handler: function() {
                                    // this.send(cfg);
                                },
                            },
                        ]
                    },
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

    health: function(value, dispatch) {
        this._health = value;
        return this._health;
    },

    observerCIRDIR: function(value) {
        if(value) {
            this.readView(value);
            Ext.getCmp('formeditor').enable();
            Ext.getCmp('btnsalvar').enable();
            Ext.getCmp('btnsalvareenviar').enable();
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
            Ext.getCmp('formeditor').disable();
            Ext.getCmp('btnsalvar').disable();
            Ext.getCmp('btnsalvareenviar').disable();
        }
    },

    readView: function(health) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        var rest = this.getGrid().factoryRestful();
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                health: health
            },
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var me = this;
                if(rst.success) {
                    Ext.getCmp('editor').setValue(rst.evaluation);
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
        var value = this.employee(cfg);
        this.getGrid(cfg).setFilterProperty('evaluator__pk', value);
    },

    autoSelectionEmployee: function(cfg) {
        if(this.employee(cfg) === undefined) {
            var rest = Ext._create('corregedoria.cirdir.EmployeeRestful');
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
                title: 'Avaliação - Vc é Único'
            }
        );
        Ext.apply(
            cfg,
            {
                layout: 'border',
                // border: false,
                items: [
                    this.getBoxPanel(cfg),
                    this.getTilePanel(cfg)
                ],
            }
        );
        corregedoria.cirdir.health.healtharea.attendance.Manage.superclass.constructor.call(this, cfg);
        this.autoSelectionEmployee(cfg);
        this.observerCIRDIR();
    },
});
