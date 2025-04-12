Ext._define('corregedoria.cirdir.PrivateLogWindow', {
    extend: 'core.RestfulWindow',

    height: 550,

    getPrivateLogGrid: function(item) {
        if(!this._privatelogGrid)
            this._privatelogGrid = Ext._create('corregedoria.cirdir.privatelog.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: false,
                height: 420,
                columnAction: false,
                hideItemsToolbar:['edit', 'remove', 'download', '-', 'search'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                params: {
                  'controlinformation': item.params.controlinformation,
                  'mainGrid': item.params.mainGrid,
              },
              doubleClickHandler: function(grid) { },
           });
        return this._privatelogGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 125,
                        items: [
                            {
                                xtype:'fieldset',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                items:[
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'employee',
                                                hideLabel: true,
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    this.getPrivateLogGrid(cfg),
                ]
            });
        }
        return this._formPanel;
    },

    getButtons: function() {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                      this.close();
                    }
                }
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Log Privado',
                modal: true,
                resizable: false,
                border: false,
                width: 1000,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(cfg),
            }
        );

        corregedoria.cirdir.PrivateLogWindow.superclass.constructor.call(this, cfg);
        if (cfg) {
            this.getFormPanel(cfg).getForm().setValues({
                employee: cfg.params.employee,
            });
            this._privatelogGrid.setFilterProperty('controlinformation_id', cfg.params.controlinformation, 100);
        }
    },

});
