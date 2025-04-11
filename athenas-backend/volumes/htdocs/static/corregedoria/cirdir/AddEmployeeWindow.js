
Ext._define('corregedoria.cirdir.AddEmployeeWindow', {
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
                rest: "corregedoria.cirdir.EmployeeRestful",
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
                labelWidth: 50,
                border: false,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 25,
                                columnWidth: 0.2,
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
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 60,
                                columnWidth: 0.80,
                                items: [
                                  this.getEmployeeField(),
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 1,
                        items: [
                            {
                                xtype:'fieldset',
                                title: 'Importar abas...',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                items:[
                                  {
                                      xtype:'panel',
                                      autoHeight:true,
                                      layout: 'column',
                                      items: [
                                          {
                                              xtype:'panel',
                                              autoHeight:true,
                                              layout: 'form',
                                              columnWidth: 0.34,
                                              items: [
                                                  {
                                                      xtype: 'checkbox',
                                                      name: 'total',
                                                      boxLabel: 'Todos',
                                                      listeners: {
                                                          scope: this,
                                                          check: function(item, checked) {
                                                              this.getFormPanel().getForm().findField('address').setValue(item.checked);
                                                              this.getFormPanel().getForm().findField('teaching').setValue(item.checked);
                                                              this.getFormPanel().getForm().findField('property').setValue(item.checked);
                                                              this.getFormPanel().getForm().findField('debits').setValue(item.checked);
                                                              this.getFormPanel().getForm().findField('health').setValue(item.checked);
                                                          },
                                                      },
                                                  },
                                                  {
                                                      xtype: 'checkbox',
                                                      name: 'address',
                                                      boxLabel: 'Residência',
                                                  },

                                              ]
                                          },
                                          {
                                              xtype:'panel',
                                              autoHeight:true,
                                              layout: 'form',
                                              columnWidth: 0.33,
                                              items: [
                                                  {
                                                      xtype: 'checkbox',
                                                      name: 'teaching',
                                                      boxLabel: 'Docência',
                                                  },
                                                  {
                                                      xtype: 'checkbox',
                                                      name: 'property',
                                                      boxLabel: 'Bens e Direitos',
                                                  },
                                              ]
                                          },
                                          {
                                              xtype:'panel',
                                              autoHeight:true,
                                              layout: 'form',
                                              columnWidth: 0.33,
                                              items: [
                                                  {
                                                      xtype: 'checkbox',
                                                      name: 'debits',
                                                      boxLabel: 'Dívidas e Ônus Reais',
                                                  },
                                                  {
                                                      xtype: 'checkbox',
                                                      name: 'health',
                                                      boxLabel: 'Saúde',
                                                  },
                                              ]
                                          },
                                      ]
                                  },
                                ]
                            },
                        ]
                    },
                ]
        });
        return this._formPanel;
    },

    addEmployeeYear: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Adicionando membro...'});
        if (values) {
            mask.show();
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('CIRDIRControlInformation', 'add_employeeyear'),
                callback: function() {
                    cfg.params.mainGrid.getStore().reload();
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Adicionando membro',
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
                        title: 'Adicionando membro',
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
                      text: 'Adicionar',
                      scope: this,
                      handler: function() {
                        this.addEmployeeYear(cfg);
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
                title: 'Adicionar Integrante',
                modal: true,
                resizable: false,
                border: false,
                width: 600,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: this.getButtons(cfg),
            }
        );
        corregedoria.cirdir.AddEmployeeWindow.superclass.constructor.call(this, cfg);
    }
});
