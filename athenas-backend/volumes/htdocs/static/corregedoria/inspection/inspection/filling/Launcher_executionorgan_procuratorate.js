Ext._define('corregedoria.inspection.inspection.filling.Launcher_executionorgan_procuratorate', {
    extend: 'Ext.Window',

    store: function(cfg) {
      if (cfg) {
          if (cfg.values.frame) {
              if (cfg.values.frame == 'procuratorate') {
                  this.storeProcuratorate(cfg);
              }
              if (cfg.values.frame == 'structure') {
                  this.storeStructure(cfg);
              }
              if (cfg.values.frame == 'generalobservations') {
                  this.storeGeneralObservations(cfg);
              }
              if (cfg.values.frame == 'attachments') {
                  this.storeAttachments(cfg);
              }
          } else {
              this.storeProcuratorate(cfg);
              this.storeStructure(cfg);
              this.storeGeneralObservations(cfg);
              this.storeAttachments(cfg);
          }
      }
    },

    storeProcuratorate: function(cfg) {
        this._storeProcuratorate = Ext._create('Ext.data.Store', {
            id: 'storeProcuratorate',
            autoLoad: true,
            proxy: Ext._create('Ext.data.HttpProxy', {
                url: core.callAction('INSPECTIONInspection', 'getProcuratorate')
            }),
            baseParams: {
                inspection_id: cfg.values.inspection_id,
            },
            reader: Ext._create('Ext.data.JsonReader', {
                totalProperty: 'count',
                root: 'collection',
                fields: [
                    {type: "auto", name: "ins_tj_session"},
                    {type: "auto", name: "ins_tj_sessions_civil"},
                    {type: "auto", name: "ins_tj_sessions_criminal"},
                    {type: "auto", name: "ins_tj_sessions_administrative"},
                    {type: "auto", name: "ins_collegiate_organ_session"},
                    {type: "auto", name: "ins_number_collegiate_organ_session"},
                    {type: "auto", name: "ins_commissions_session"},
                    {type: "auto", name: "mp_observation"},
                ]
            })
        });
        storeProcuratorateCache = this._storeProcuratorate;
        this._storeProcuratorate.load({
            'scope': this,
            'callback': function() {
                if (storeProcuratorateCache.data.items["0"]) {
                    this.getFormPanel().getForm().setValues({
                        ins_tj_session: storeProcuratorateCache.data.items["0"].data.ins_tj_session,
                        ins_tj_sessions_civil: storeProcuratorateCache.data.items["0"].data.ins_tj_sessions_civil,
                        ins_tj_sessions_criminal: storeProcuratorateCache.data.items["0"].data.ins_tj_sessions_criminal,
                        ins_tj_sessions_administrative: storeProcuratorateCache.data.items["0"].data.ins_tj_sessions_administrative,
                        ins_collegiate_organ_session: storeProcuratorateCache.data.items["0"].data.ins_collegiate_organ_session,
                        ins_number_collegiate_organ_session: storeProcuratorateCache.data.items["0"].data.ins_number_collegiate_organ_session,
                        ins_commissions_session: storeProcuratorateCache.data.items["0"].data.ins_commissions_session,
                        mp_observation: storeProcuratorateCache.data.items["0"].data.mp_observation,
                    });
                }
            }
        });
        return this._storeProcuratorate;
    },

    getTabProcuratorate: function(cfg) {
        if(!this._functionalPerformance)
            this._functionalPerformance = new corregedoria.inspection.inspection.filling.procuratorate.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                    thiswindow: this,
                }
            });
        return this._functionalPerformance;
    },

    storeStructure: function(cfg) {
        if(!this._storeStructure) {
            this._storeStructure = Ext._create('Ext.data.Store', {
                autoLoad: true,
                proxy: Ext._create('Ext.data.HttpProxy', {
                    url: core.callAction('INSPECTIONInspection', 'getStructure')
                }),
                baseParams: {
                    inspection_id: cfg.values.inspection_id,
                },
                reader: Ext._create('Ext.data.JsonReader', {
                    totalProperty: 'count',
                    root: 'collection',
                    fields: [
                        {type: "auto", name: "est_deficiency"},
                    ]
                })
            });
            storeStructureCache = this._storeStructure;
            this._storeStructure.load({
                'scope': this,
                'callback': function() {
                    this.getFormPanel().getForm().setValues({
                        est_deficiency: storeStructureCache.data.items["0"].data.est_deficiency,
                    });
                }
            });
        }
        return this._storeStructure;
    },

    getTabStructure: function(cfg) {
        if(!this._structure)
            this._structure = new corregedoria.inspection.inspection.filling.structure.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                }
            });
        return this._structure;
    },

    storeGeneralObservations: function(cfg) {
        if(!this._storeGeneralObservations) {
            this._storeGeneralObservations = Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONInspection', 'getGeneralObservations')
                    }),
                    baseParams: {
                        inspection_id: cfg.values.inspection_id,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "go_generalobservations"},
                        ]
                    })
                });
                storeGeneralObservations = this._storeGeneralObservations;
                this._storeGeneralObservations.load({
                    'scope': this,
                    'callback': function() {
                        this.getFormPanel().getForm().setValues({
                            go_generalobservations: storeGeneralObservations.data.items["0"].data.go_generalobservations,
                        });
                    }
                });
            }
            return this._storeGeneralObservations;
    },

    getTabGeneralObservations: function(cfg) {
        if(!this._generalObservations)
            this._generalObservations = new corregedoria.inspection.inspection.filling.generalobservations.Launcher({
                title: 'OBSERVAÇÕES/SUGESTÕES',
                values: {
                    inspection_id: cfg.values.inspection_id,
                }
            });

        return this._generalObservations;
    },

    getTabAttachments: function(cfg) {
        if(!this._attachments)
            this._attachments = new corregedoria.inspection.inspection.filling.attachments.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                }
            });
        return this._attachments;
    },

    getFrames: function(cfg) {
        ret = [];
        if (cfg.values.frame) {
            if (cfg.values.frame == 'procuratorate') {
                ret = [ this.getTabProcuratorate(cfg) ];
            }
            if (cfg.values.frame == 'structure') {
                ret = [ this.getTabStructure(cfg) ];
            }
            if (cfg.values.frame == 'generalobservations') {
                ret = [ this.getTabGeneralObservations(cfg) ];
            }
        } else {
            ret = [
                this.getTabProcuratorate(cfg),
                this.getTabStructure(cfg),
                this.getTabGeneralObservations(cfg),
             ];
        }
        return ret;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                id: 'formPanel',
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 125,
                        items: [

                            {
                                xtype:'fieldset',
                                title: 'Inspeção/Correição',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                width: 1170,
                                items:[
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 110,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'execution_organ',
                                                fieldLabel: 'Órgão de Execução',
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 198,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'employee',
                                                fieldLabel: 'Procurador/Promotor Responsável',
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 198,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'responsible',
                                                fieldLabel: 'Procurador/Promotor Inspecionado',
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 155,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'inspection_date',
                                                fieldLabel: 'Data da Inspeção/Correição',
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'tabpanel',
                        activeTab: 0,
                        height: 600,
                        border: false,
                        items: [
                            this.getFrames(cfg),
                        ],
                    },
                ]
            });

        return this._formPanel;
    },

    getFieldsProcuratorate: function(values) {
        ret = {
            ins_tj_session: values.ins_tj_session,
            ins_tj_sessions_civil: values.ins_tj_sessions_civil,
            ins_tj_sessions_criminal: values.ins_tj_sessions_criminal,
            ins_tj_sessions_administrative: values.ins_tj_sessions_administrative,
            ins_collegiate_organ_session: values.ins_collegiate_organ_session,
            ins_number_collegiate_organ_session: values.ins_number_collegiate_organ_session,
            ins_commissions_session: values.ins_commissions_session,
            mp_observation: values.mp_observation,
        };
        return ret;
    },

    getFieldsStructure: function(values) {
        ret = {
            est_deficiency: values.est_deficiency
        };
        return ret;
    },

    getFieldsGeneralObservations: function(values) {
        ret = {
            go_generalobservations: values.go_generalobservations,
        };
        return ret;
    },


    getFieldsAttachments: function(values) {
        ret = {

        };
        return ret;
    },

    getSaveFields: function(cfg, values) {
      save = { inspection_id: cfg.values.inspection_id, instance: cfg.values.instance, frame: cfg.values.frame };
      if (cfg.values.frame) {
          if (cfg.values.frame == 'procuratorate') {
              ret = Object.assign(save, this.getFieldsProcuratorate(values));
          }
          if (cfg.values.frame == 'structure') {
              ret = Object.assign(save, this.getFieldsStructure(values));
          }
          if (cfg.values.frame == 'generalobservations') {
              ret = Object.assign(save, this.getFieldsGeneralObservations(values));
          }
      } else {
          ret = Object.assign(save, this.getFieldsProcuratorate(values), this.getFieldsStructure(values), this.getFieldsGeneralObservations(values), this.getFieldsAttachments(values) );
      }
      return ret;
    },

    save: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados da inspeção...'});
        Ext.Msg.show({
            title: 'Salvar Inspeção/Correição',
            msg: 'Tem certeza que deseja persistir inspeção?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONInspection', 'save'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Salvar Inspeção/Correição',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                        } else {
                            Ext.Msg.show({
                                title: 'Salvar Inspeção/Correição',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Salvar Inspeção/Correição',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    },
                    params: this.getSaveFields(cfg, values),
                });
            }
        });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Gestor de Inspeções/Correições - ÓRGÃOS DE EXECUÇÃO',
            width: 1200,
            height: 800,
        });

        Ext.apply(cfg, {
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: [
                {
                    text: '<b>Salvar</b>',
                    scope: this,
                    handler: function() { this.save(cfg); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        cfg.values.gridInspection.getStore().reload();
                        this.close();
                    }
                }
            ]
        });
        corregedoria.inspection.inspection.filling.Launcher_executionorgan_procuratorate.superclass.constructor.call(this, cfg);
        if (cfg) {
          this.getFormPanel().getForm().setValues({
              employee: cfg.values.employee,
              responsible: cfg.values.responsible,
              execution_organ: cfg.values.execution_organ,
              inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,
          });
          this.store(cfg);
        }
    }
});
