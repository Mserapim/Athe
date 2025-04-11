var storeCache = {};

Ext._define('raf.quiz.TaxonomyWindow', {
    extend: 'Ext.Window',

    factoryStore: function(cfg) {
        if(!this._factoryStore) {
            this._factoryStore = Ext._create('Ext.data.Store', {
                  autoLoad: true,
                  proxy: Ext._create('Ext.data.HttpProxy', {
                      url: core.callAction('RAFQuiz', 'get_taxonomy')
                  }),
                  baseParams: {
                      autoreference: cfg.params.autoreference,
                  },
                  reader: Ext._create('Ext.data.JsonReader', {
                      totalProperty: 'count',
                      root: 'collection',
                      fields: [
                          {name: 'processo', type: 'auto'},
                      ]
                  })
              });
              this._factoryStore.load({
                  'scope': this,
                  'callback': function() {
                      // this.getFormPanel().getForm().setValues(storeCache.data.items["0"].data);
                  }
              })

          }
          return this._factoryStore;

    },


    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                  {
                      id:'dataeproc-identidicacao-fieldset',
                      xtype:'fieldset',
                      title: 'Identificação',
                      collapsible: false,
                      autoHeight:true,
                      items:[
                          {
                              id: 'dataeproc-panel-processo-field',
                              allowBlank: true,
                              width: 750,
                              // disabled: true,
                              fieldLabel: "Processo",
                              name: "processo",
                              xtype: "textfield"
                          },
                          {
                              id: 'dataeproc-panel-classe-field',
                              allowBlank: true,
                              width: 750,
                              height: 50,
                              // disabled: true,
                              fieldLabel: "Classe",
                              name: "classe",
                              xtype: "textarea"
                          },
                          {
                              id: 'dataeproc-panel-assuntoprincipal-field',
                              allowBlank: true,
                              width: 750,
                              // disabled: true,
                              fieldLabel: "Assunto",
                              name: "assuntoprincipal",
                              xtype: "textfield"
                          },
                      ]
                  },
                  {
                      id:'dataeproc-movimento-fieldset',
                      xtype:'fieldset',
                      title: 'Movimento',
                      collapsible: false,
                      autoHeight:true,
                      items:[
                          {
                              id: 'dataeproc-panel-movimento-field',
                              allowBlank: true,
                              width: 750,
                              // disabled: true,
                              fieldLabel: "Movimento",
                              name: "movimento",
                              xtype: "textfield"
                          },
                          {
                              id: 'dataeproc-panel-datamovimento-field',
                              allowBlank: true,
                              width: 750,
                              // disabled: true,
                              fieldLabel: "Data/Hora:",
                              name: "datamovimento",
                              xtype: "textfield"
                          },
                      ]
                  },
                ]
            });
        return this._formPanel;
    },

    getButtons: function(cfg) {
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

        Ext.applyIf(cfg, {
            title: 'EPROC - Atuação Ministerial',
            width: 910,
            height: 325,
        });

        Ext.apply(cfg, {
            ds: this.factoryStore(cfg),
            items: this.getFormPanel(),
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

        raf.autoreference.DataEprocWindow.superclass.constructor.call(this, cfg);
        storeCache = this.factoryStore(cfg);
    }
});
