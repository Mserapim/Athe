
Ext._define('raf.management.ImportEproc2AthenasWindow', {
    extend: 'core.RestfulWindow',

    getValues: function() {
        var values = this.getFormPanel().getForm().getValues();
        values.validate = true;
        values.initialdate = values.inicio.substring(6,10) + '-' + values.inicio.substring(3,5) + '-' + values.inicio.substring(0,2);
        values.finaldate = values.fim.substring(6,10) + '-' + values.fim.substring(3,5) + '-' + values.fim.substring(0,2);
        return values;
    },

    getEmployeeField: function() {
        if(!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Membro',
                allowBlank: true,
                rest: "raf.EmployeeRestful",
                name: "employee",
                disabled: false,
                preFilter: [
                    {property: 'tipo', value: 'M', stage: 100},
                ],
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'ativo'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                }
            });
        }
        return this._employeeField;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 50,
                border: false,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Importação',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                defaults: {
                                    labelAlign: 'left',
                                    style: 'margin-right: 15px;',
                                },
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 30,
                                        items: [
                                            {
                                                xtype: 'datefield',
                                                fieldLabel: 'Início',
                                                name: 'inicio',
                                                allowBlank: false,
                                                blankText: 'DATA DE INÍCIO precisa ser preenchida.',
                                            },
                                        ]

                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 30,
                                        items: [
                                            {
                                                xtype: 'datefield',
                                                fieldLabel: 'Final',
                                                name: 'fim',
                                                allowBlank: false,
                                                blankText: 'DATA FINAL precisa ser preenchida.',
                                            },
                                        ]

                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 55,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'combobox',
                                                fieldLabel: 'Instância',
                                                hiddenName: 'instancia',
                                                width: 200,
                                                store: [
                                                    [0, 'TODAS AS INSTÂNCIAS'],
                                                    [1, '1ª INSTÂNCIA'],
                                                    [2, '2ª  INSTÂNCIA'],
                                                ],
                                                allowBlank: false,
                                                value: 0,
                                            },
                                        ]

                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Opcional',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                            this.getEmployeeField(),
                        ]
                    }
                ]
        });
        return this._formPanel;
    },

    importarEProc: function() {
        var values = this.getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Importação de documento(s) do e-Proc...'});
        if (values.validate) {
            mask.show();
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('RAFFunctionalActivityReport', 'importEproc2AthenasRAF'),
                callback: function() {
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Importação de documento(s) do e-Proc',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    // this.close();
                    core.invokeCallback((this.callback || {}).success);
                },
                failure: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Importação de documento(s) do e-Proc',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                params: {
                    initialdate: values.initialdate,
                    finaldate: values.finaldate,
                    employee: values.employee,
                    instancia: values.instancia
                },
            });
        } else {
            Ext.Msg.show({
              title: 'Importação de documento(s) do e-Proc',
              msg: values.message,
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Importar',
                    scope: this,
                    handler: function() { this.importarEProc(); }
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
                title: 'Importação de documento(s) do e-Proc/e-Ext',
                modal: true,
                resizable: false,
                border: false,
                width: 700,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: this.getButtons(cfg),
            }
        );
        raf.management.ImportEproc2AthenasWindow.superclass.constructor.call(this, cfg);
    }
});
