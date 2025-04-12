Ext._define('corregedoria.inspection.inspection.filling.structure.structureexternalpeoples.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.structure.structureexternalpeoples.Restful',

    width: 600,

    setSelectValues: function(sep_name, sep_function, sep_category) {
      a = this.getFormPanel().find('name', 'name')[0];
      a.setValue(sep_name);
      b = this.getFormPanel().find('name', 'function')[0];
      b.setValue(sep_function);
      c = this.getFormPanel().find('name', 'category')[0];
      c.setValue(sep_category);
    },

    getExternalEmployeesField: function(cfg) {
        if(!this._externalEmployeesField) {
            this._externalEmployeesField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Servidor Externo",
                allowBlank: true,
                rest: "corregedoria.inspection.inspection.filling.structure.personalmovement.ExternalPeoplesRestful",
                name: "personal_movement",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                    params: {inspection: cfg.values.inspection_id},
                },
            });
            this._externalEmployeesField.getComboField().addListener('select', function(combo, record, index) { this.setSelectValues(record.data.employee_unicode, record.data.occupation_unicode, record.data.category); }, this);
        }
        return this._externalEmployeesField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                  {
                      xtype:'fieldset',
                      title: 'Pesquisar',
                      collapsible: false,
                      collapsed: false,
                      autoHeight:true,
                      // width: 1115,
                      items:[
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'form',
                              labelWidth: 97,
                              items: [
                                  this.getExternalEmployeesField(cfg),
                              ],
                          },
                      ]
                  },
                  {
                      xtype:'fieldset',
                      title: 'Cadastro',
                      collapsible: false,
                      collapsed: false,
                      autoHeight:true,
                      // width: 1115,
                      items:[
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'form',
                              labelWidth: 35,
                              items: [
                                    {
                                        xtype: 'textfield',
                                        // id: 'sep_name',
                                        fieldLabel: 'Nome',
                                        name: 'name',
                                        width: 510,
                                    },
                                ],
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 40,
                                items: [
                                    {
                                        xtype: 'textfield',
                                        // id: 'sep_function',
                                        fieldLabel: 'Função',
                                        name: 'function',
                                        width: 505,
                                    },
                                ],
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 55,
                                items: [
                                    {
                                        xtype: 'textfield',
                                        // id: 'sep_category',
                                        fieldLabel: 'Categoria',
                                        name: 'category',
                                        width: 490,
                                    },
                                ],
                            },
                        ],
                    },
                ]
            });

        return this._formPanel;
    },
});
