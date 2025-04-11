Ext._define('corregedoria.cirdir.address.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.address.Restful',

    width: 900,

    getAddressField: function(cfg) {
        if(!this._addressField) {
            this._addressField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Endereço',
                allowBlank: true,
                rest: "rh.endereco.EnderecoRestful",
                name: "ref_address",
                disabled: false,
                preFilter: [
                  { property: 'person_id', value: cfg.values.person_id, stage: 100 },
                ],
                gridConfig: {
                    columnAction: false,
                    preFilter: [
                      { property: 'person_id', value: cfg.values.person_id, stage: 100 },
                    ],
                    params: {
                        person: cfg.values.person_id
                    }
                }
            });
        }
        return this._addressField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
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
                              labelWidth: 110,
                              columnWidth: 0.27,
                              items: [
                                  {
                                    xtype: 'choicefield',
                                    fieldLabel: 'Tipo de Residência',
                                    hiddenName: 'type_residence',
                                    width: 100,
                                    choiceId: 'cirdir.TYPE_RESIDENCE',
                                  },
                              ]
                          },
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'form',
                              labelWidth: 60,
                              columnWidth: 0.73,
                              items: [
                                  this.getAddressField(cfg)
                              ]
                          },
                      ]
                  },
                  {
                      xtype:'panel',
                      autoHeight:true,
                      layout: 'column',
                      items: [
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'form',
                              labelWidth: 110,
                              columnWidth: 0.33,
                              items: [
                                {
                                    xtype: 'datefield',
                                    fieldLabel: 'Início da Residência',
                                    width: 115,
                                    name: 'start_date',
                                },
                              ]
                          },
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'form',
                              labelWidth: 1,
                              columnWidth: 0.67,
                              items: [
                                {
                                    xtype: 'checkbox',
                                    name: 'authorization_reside_outside',
                                    boxLabel: 'Possui autorização do CSMP de residir fora da comarca. ',
                                },
                              ]
                          },
                      ]
                  },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
        });
        corregedoria.cirdir.address.Window.superclass.constructor.call(this, cfg);
    },

});
