
Ext._define('corregedoria.cirdir.AddYearWindow', {
    extend: 'core.RestfulWindow',

    getFormPanel: function() {
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
                                labelWidth: 62,
                                columnWidth: 0.40,
                                items: [
                                  {
                                      xtype: 'textfield',
                                      fieldLabel: 'Último ano',
                                      width: 70,
                                      name: 'lastyear',
                                      readOnly: true,
                                  },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 55,
                                columnWidth: 0.60,
                                items: [
                                  {
                                      xtype: 'textfield',
                                      fieldLabel: 'Novo ano',
                                      width: 70,
                                      name: 'newyear',
                                      readOnly: true,
                                  },
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
                                              columnWidth: 0.30,
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
                                                              // this.getFormPanel().getForm().findField('health').setValue(item.checked);
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
                                              columnWidth: 0.30,
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
                                              columnWidth: 0.4,
                                              items: [
                                                  {
                                                      xtype: 'checkbox',
                                                      name: 'debits',
                                                      boxLabel: 'Dívidas e Ônus Reais',
                                                  },
                                                  {
                                                      xtype: 'checkbox',
                                                      name: 'health',
                                                      hidden: true,
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

    addNewYear: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Adicioando novo ano...'});
        if (values) {
            mask.show();
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('CIRDIRControlInformation', 'add_newyear'),
                callback: function() {
                    cfg.params.mainGrid.getStore().reload();
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Adicionando novo ano',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    this.close();
                    core.invokeCallback((this.callback || {}).success);
                },
                failure: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Adicionando novo ano',
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
                        this.addNewYear(cfg);
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
                title: 'Adicionar ano',
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
        corregedoria.cirdir.AddYearWindow.superclass.constructor.call(this, cfg);
        if (cfg.params.lastyear) {
            this.getFormPanel().getForm().setValues(
              {
                lastyear: cfg.params.lastyear,
                newyear: cfg.params.lastyear+1,
              }
            );
        } else {
          this.getFormPanel().getForm().findField('newyear').setReadOnly(false);
        }
    }
});
