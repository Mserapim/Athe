
Ext._define('corregedoria.inspection.inspection.filling.procuratorate.Launcher', {
    extend: 'Ext.Panel',

    getProcForQualAnalysisOfThePartsProcuratorateGrid: function(cfg) {
        if(!this._procForQualAnalysisOfThePartsProcuratorateGrid) {
            this._procForQualAnalysisOfThePartsProcuratorateGrid = Ext._create('corregedoria.inspection.inspection.filling.procuratorate.procforqualanalysisofthepartsprocuratorate.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 150,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},
            });
            this.getProcForQualAnalysisOfThePartsProcuratorateGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._procForQualAnalysisOfThePartsProcuratorateGrid;
    },

    getProceduralMovementReceived: function(cfg) {
        if(!this._proceduralMovementReceived) {
            this._proceduralMovementReceived = Ext._create('corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementreceived.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 150,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},
            });
            this.getProceduralMovementReceived().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._proceduralMovementReceived;
    },

    getProceduralMovementReturned: function(cfg) {
        if(!this._proceduralMovementReturned) {
            this._proceduralMovementReturned = Ext._create('corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementreturned.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 150,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},

            });
            this.getProceduralMovementReturned().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._proceduralMovementReturned;
    },

    getProceduralMovementOuCourtLawsuit: function(cfg) {
        if(!this._proceduralMovementOutCourtLawsuit) {
            this._proceduralMovementOutCourtLawsuit = Ext._create('corregedoria.inspection.inspection.filling.procuratorate.proceduralmovementoutcourtlawsuit.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 150,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},
            });
            this.getProceduralMovementOuCourtLawsuit().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._proceduralMovementOutCourtLawsuit;
    },

   getTJSessions: function(cfg) {
       if(!this._tjSessionsForm) {
           this._tjSessionsForm = Ext._create('Ext.form.FieldSet', {
               title: 'Sessões do Tribunal de Justiça',
               collapsible: true,
               collapsed: false,
               autoHeight:true,
               labelWidth: 80,
               items:[
                   {
                       xtype:'panel',
                       autoHeight:true,
                       layout: 'form',
                       labelWidth: 250,
                       items: [
                           {
                               fieldLabel: 'Participou de sessões no Tirbunal de Justiça',
                               xtype: 'combo',
                               id: 'ins_tj_session',
                               hiddenName: 'ins_tj_session',
                               width: 100,
                               editable: false,
                               triggerAction: 'all',
                               store: [
                                   [1, ''],
                                   [2, 'SIM'],
                                   [3, 'NÃO'],
                               ],
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
                               labelWidth: 150,
                               columnWidth: 0.33,
                               items: [
                                   {
                                       fieldLabel: 'Número de sessões cíveis',
                                       xtype: 'numberfield',
                                       name: 'ins_tj_sessions_civil',
                                       width: 150,
                                   }
                               ]
                           },
                           {
                               xtype:'panel',
                               autoHeight:true,
                               layout: 'form',
                               labelWidth: 170,
                               columnWidth: 0.33,
                               items: [
                                   {
                                       fieldLabel: 'Número de sessões criminais',
                                       xtype: 'numberfield',
                                       name: 'ins_tj_sessions_criminal',
                                       width: 150,
                                   }
                               ]
                           },
                           {
                               xtype:'panel',
                               autoHeight:true,
                               layout: 'form',
                               labelWidth: 205,
                               columnWidth: 0.34,
                               items: [
                                   {
                                       fieldLabel: 'Número de sessões administrativas',
                                       xtype: 'numberfield',
                                       name: 'ins_tj_sessions_administrative',
                                       width: 150,
                                   }
                               ]
                           },
                       ]
                   },
               ]
           });
       }
       return this._tjSessionsForm;
   },

   getCollegiateOrganSessions: function(cfg) {
       if(!this._collegiateOrganSessionsForm) {
           this._collegiateOrganSessionsForm = Ext._create('Ext.form.FieldSet', {
               title: 'Sessões nos Órgãos Colegiados',
               collapsible: true,
               collapsed: false,
               autoHeight:true,
               labelWidth: 80,
               items:[
                   {
                       xtype:'panel',
                       autoHeight:true,
                       layout: 'form',
                       labelWidth: 80,
                       items: [
                           {
                               xtype:'panel',
                               autoHeight:true,
                               layout: 'form',
                               labelWidth: 250,
                               items: [
                                   {
                                       fieldLabel: 'Participou de sessões em Órgãos Colegiados',
                                       xtype: 'combo',
                                       id: 'ins_collegiate_organ_session',
                                       hiddenName: 'ins_collegiate_organ_session',
                                       width: 100,
                                       editable: false,
                                       triggerAction: 'all',
                                       store: [
                                           [1, ''],
                                           [2, 'SIM'],
                                           [3, 'NÃO'],
                                       ],
                                   },
                               ]
                           },
                           {
                               xtype:'panel',
                               autoHeight:true,
                               layout: 'form',
                               labelWidth: 115,
                               items: [
                                   {
                                       fieldLabel: 'Número de sessões',
                                       xtype: 'numberfield',
                                       name: 'ins_number_collegiate_organ_session',
                                       width: 150,
                                   }
                               ]
                           },
                       ]
                   },
               ]
           });
       }
       return this._collegiateOrganSessionsForm;
   },

   getCommissionSessions: function(cfg) {
       if(!this._commissionSessionsForm) {
           this._commissionSessionsForm = Ext._create('Ext.form.FieldSet', {
               title: 'Reuniões de Comissões',
               collapsible: true,
               collapsed: false,
               autoHeight:true,
               labelWidth: 80,
               items:[
                   {
                       xtype:'panel',
                       autoHeight:true,
                       layout: 'form',
                       labelWidth: 80,
                       items: [
                           {
                               xtype:'panel',
                               autoHeight:true,
                               layout: 'form',
                               labelWidth: 210,
                               items: [
                                   {
                                       fieldLabel: 'Participou de reuniões de comissões',
                                       xtype: 'combo',
                                       id: 'ins_commissions_session',
                                       hiddenName: 'ins_commissions_session',
                                       width: 100,
                                       editable: false,
                                       triggerAction: 'all',
                                       store: [
                                           [1, ''],
                                           [2, 'SIM'],
                                           [3, 'NÃO'],
                                       ],
                                   },
                               ]
                           },
                       ]
                   },
               ]
           });
       }
       return this._commissionSessionsForm;
   },

    getProceduralMovementForm: function(cfg) {
        if(!this._proceduralMovementForm) {
            this._proceduralMovementForm = Ext._create('Ext.form.FieldSet', {
                title: 'Movimentação Processual',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                labelWidth: 55,
                width: 1130,
                items:[
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        style: {margin: '10px', fontSize: '13px'},
                        items: [
                            {
                                xtype: 'label',
                                text: 'RECEBIDOS',
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            this.getProceduralMovementReceived(cfg),
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        style: {margin: '10px', fontSize: '13px'},
                        items: [
                            {
                                xtype: 'label',
                                text: 'DEVOLVIDOS',
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            this.getProceduralMovementReturned(cfg),
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        style: {margin: '10px', fontSize: '13px'},
                        items: [
                            {
                                xtype: 'label',
                                text: 'PROCEDIEMNTOS EXTRAJUDICIAIS (quando houver)',
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            this.getProceduralMovementOuCourtLawsuit(cfg),
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 80,
                        style: {marginTop: '10px'},
                        items: [
                            {
                                fieldLabel: 'Observações',
                                xtype: 'textarea',
                                name: 'mp_observation',
                                width: 1020,
                                height: 125,
                            }
                        ]
                    },
                ]
            });
        }
        return this._proceduralMovementForm;
    },

    getQuallitativeAnalysisOfThePartsProcuratorateForm: function(cfg) {
        if(!this._qualitativeAnalysisOfThePartsProcuratorateForm) {
            this._qualitativeAnalysisOfThePartsProcuratorateForm = Ext._create('Ext.form.FieldSet', {
                title: '3. Análise Qualitativa das Peças',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                labelWidth: 55,
                width: 1130,
                items:[
                    this.getProcForQualAnalysisOfThePartsProcuratorateGrid(cfg)
                ]
            });
        }
        return this._qualitativeAnalysisOfThePartsProcuratorateForm;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'CONTROLE DE ATIVIDADES',
            layout: 'form',
            frame: true,
            height: 575,
            border: false,
            autoScroll: true,
            overflow: 'auto',
            bodyStyle: 'padding: 5px',
            items: [
                this.getTJSessions(cfg),
                this.getCollegiateOrganSessions(cfg),
                this.getCommissionSessions(cfg),
                this.getProceduralMovementForm(cfg),
                this.getQuallitativeAnalysisOfThePartsProcuratorateForm(cfg),
            ],
        });

        Ext.apply(cfg, {

        });

        corregedoria.inspection.inspection.filling.procuratorate.Launcher.superclass.constructor.call(this, cfg);

    }
});
