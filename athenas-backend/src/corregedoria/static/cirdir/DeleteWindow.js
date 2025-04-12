
Ext._define('corregedoria.cirdir.DeleteWindow', {
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

    getEmployeeField: function() {
        if(!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Integrante',
                allowBlank: true,
                rest: "raf.EmployeeRestful",
                name: "employee",
                disabled: false,
                preFilter: [
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

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 60,
                border: false,
                items: [
                    {
                      fieldLabel: 'Ano',
                      xtype: 'combo',
                      hiddenName: 'year',
                      width: 75,
                      editable: false,
                      triggerAction: 'all',
                      store: this.storeYear(cfg),
                      valueField: 'key',
                      displayField: 'value',
                      allowBlank: true,
                    },
                    this.getEmployeeField(),
                ]
        });
        return this._formPanel;
    },

    delete: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        msg = '';
        if (values.year && values.employee) {

            msg = 'Tem certeza que deseja remover os dados de <b>' +this.getFormPanel().getForm().findField('employee')._comboField.lastSelectionText+ '</b>, referentes ao ano de <b>'+values.year+'</b>?';
            mask_msg = 'Removendo dados de <b>'+this.getFormPanel().getForm().findField('employee')._comboField.lastSelectionText+'</b> do ano <b>'+values.year+'</b>...';

            Ext.Msg.show({
                title: 'Remover',
                msg: msg,
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    var mask = new Ext.LoadMask(this.getEl(), {msg: 'Removendo...'});
                    if (values) {
                        mask.show();
                        Ext.Ajax.request({
                            scope: this,
                            url: core.callAction('CIRDIRControlInformation', 'delete_employeeyear'),
                            callback: function() {
                                cfg.params.mainGrid.getStore().reload();
                                mask.hide();
                            },
                            success: function(request) {
                                var rst = Ext.decode(request.responseText);
                                Ext.Msg.show({
                                    title: 'Remover',
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
                                    title: 'Remover',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            },
                            params: values,
                        });
                    }
                }
            });
        } else {
          Ext.Msg.show({
              title: 'Remover',
              msg: 'O campo <b>Ano</b> e <b>Integrante</b> devem ser preenchidos.',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
          });
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                      text: 'Remover',
                      scope: this,
                      handler: function() {
                        this.delete(cfg);
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
                title: 'Remover',
                modal: true,
                resizable: false,
                border: false,
                width: 500,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: this.getButtons(cfg),
            }
        );
        corregedoria.cirdir.DeleteWindow.superclass.constructor.call(this, cfg);
    }
});
