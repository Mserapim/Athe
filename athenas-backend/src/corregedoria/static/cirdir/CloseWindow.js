
Ext._define('corregedoria.cirdir.CloseWindow', {
    extend: 'core.RestfulWindow',

    storeYear: function(cfg) {
        if(!this._storeYear) {
            this._storeYear = Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('CIRDIRControlInformation', 'get_storeyear')
                    }),
                    baseParams: {
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "int", name: "key"},
                            {type: "str", name: "value"},
                        ]
                    })
                });
                storeYearCache = this._storeYear;
                this._storeYear.load({
                    scope: this,
                    callback: function() {

                    }
                });
            }
            return this._storeYear;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 50,
                border: false,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 190,
                        items: [
                            {
                                fieldLabel: 'Selecione o ano que deseja fechar',
                                xtype: 'combo',
                                hiddenName: 'year',
                                width: 75,
                                editable: false,
                                triggerAction: 'all',
                                store: this.storeYear(cfg),
                                valueField: 'key',
                                displayField: 'value',
                                allowBlank: true,
                            }
                        ]
                    },
                ]
        });
        return this._formPanel;
    },

    closeAll: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.criteria = cfg.params.criteria;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Fechando SRDIR...'});
        if (values) {
            mask.show();
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('CIRDIRControlInformation', 'close_all'),
                callback: function() {
                    cfg.params.mainGrid.getStore().reload();
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Fechando SDRIR',
                        msg: rst.message,
                        icon: rst.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                    if (rst.success == true) {
                        this.close();
                        core.invokeCallback((this.callback || {}).success);
                    }
                },
                failure: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Fechando SDRIR',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                params: values,
            });
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                      text: '<b>Fechar SRDIR</b>',
                      scope: this,
                      width: 125,
                      handler: function() {
                        this.closeAll(cfg);
                      }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                title: 'Fechar SRDIR',
                modal: true,
                resizable: false,
                border: false,
                width: 300,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: this.getButtons(cfg),
            }
        );
        corregedoria.cirdir.CloseWindow.superclass.constructor.call(this, cfg);
    }
});
