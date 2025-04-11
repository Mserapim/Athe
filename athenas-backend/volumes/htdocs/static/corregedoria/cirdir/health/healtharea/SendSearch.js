Ext._define('corregedoria.cirdir.health.healtharea.SendSearch', {
    extend: 'Ext.Window',

    modal: true,

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

    getEmployeeField: function(cfg) {
        if(!this._employeeField)
            this._employeeField = Ext._create('core.fields.MultiSelectField', {
                title: 'Destinatários',
                hideLabel: true,
                name: 'employee',
                hiddenName: 'employee',
                displayField: 'unicode',
                allowBlank: true,
                rest: 'raf.EmployeeRestful',
                preFilter: [
                    {property: 'ativo', value: true, stage: 100},
                ],
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'ativo'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                },
                height: 480,
                border: false
            });

        return this._employeeField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getEmployeeField(),
                ]
            });
        }
        return this._formPanel;
    },

    send: function(cfg){
        var values = this.getFormPanel().getForm().getValues();
        values.employee = this.getEmployeeField().getValues();
        if(values.employee) {
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Enviando pesquisa...'});
            Ext.Msg.show({
                title: 'Enviar pesquisa',
                msg: 'Tem certeza que deseja enviar a pesquisa?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('CIRDIRControlInformation', 'send_search'),
                        callback: function() {
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Enviar pesquisa...',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            } else {
                                Ext.Msg.show({
                                    title: 'Enviar pesquisa...',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Enviar pesquisa...',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: values,
                    });
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Enviar pesquisa...',
                msg: 'Verifique o preenchimento dos campos. Envio não efetuado.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Enviar Pesquisa',
            width: 1000,
            height: 540,
        });

        Ext.apply(cfg, {
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: [
                {
                    text: '<b>Enviar</b>',
                    scope: this,
                    handler: function() {
                        this.send(cfg);
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ]
        });
        corregedoria.cirdir.health.healtharea.SendSearch.superclass.constructor.call(this, cfg);
    }

});
