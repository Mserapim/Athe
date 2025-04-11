
Ext._define('corregedoria.inspection.inspection.filling.functionalperformance.Launcher', {
    extend: 'Ext.Panel',

    getFinalScoreOperabilityForm: function(cfg) {
        if(!this._finalScoreOperabilityForm) {
            this._finalScoreOperabilityForm = Ext._create('Ext.form.FieldSet', {
                title: 'Pontuação Operosidade',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                width: 250,
                items:[
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            {
                                xtype: 'displayfield',
                                id: 'operability_score',
                                name: 'operability_score',
                                width: '100%',
                                style: {textAlign: 'center', fontSize: '34px', fontWeight: 'bolder'},
                            },
                        ]
                    },
                ]
            });
        }
        return this._finalScoreOperabilityForm;
    },

    getRegisteredPublicAttendanceNumberForm: function(cfg) {
        if(!this._registeredPublicAttendanceNumberForm) {
            this._registeredPublicAttendanceNumberForm = Ext._create('Ext.form.FieldSet', {
                title: '1. Número de Atendimento ao Público Registrado',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                width: 850,
                items:[
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 175,
                        items: [
                            {
                                xtype: 'displayfield',
                                id: 'dpl_average',
                                name: 'dpl_average',
                                fieldLabel: 'Média de atendimento por mês',
                                style: {fontWeight: 'bold', fontSize: '14px', },
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 100,
                        items: [
                            {
                                xtype: 'displayfield',
                                id: 'dpl_score',
                                name: 'dpl_score',
                                fieldLabel: 'Pontuação obtida',
                                style: {fontWeight: 'bold', fontSize: '14px', },
                            },
                        ]
                    },
                ]
            });
        }
        return this._registeredPublicAttendanceNumberForm;
    },

    getProcForQualAnalysisOfCivilForensicPartsGrid: function(cfg) {
        if(!this._procForQualAnalysisOfCivilForensicParts) {
            this._procForQualAnalysisOfCivilForensicParts = Ext._create('corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartscivilcourtlawsuit.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 150,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},
            });
            this.getProcForQualAnalysisOfCivilForensicPartsGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
            this.getProcForQualAnalysisOfCivilForensicPartsGrid().getStore().on({
                'load': {
                    scope: this,
                    fn: function(records, options) {
                        cfg.values.thiswindow.storeFunctionalPerformance(cfg);
                    },
                },
            });
        }
        return this._procForQualAnalysisOfCivilForensicParts;
    },

    getProcForQualAnalysisOfCriminalForensicPartsGrid: function(cfg) {
        if(!this._procForQualAnalysisOfCriminalForensicParts) {
            this._procForQualAnalysisOfCriminalForensicParts = Ext._create('corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartscriminalcourtlawsuit.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 150,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},
            });
            this.getProcForQualAnalysisOfCriminalForensicPartsGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
            this.getProcForQualAnalysisOfCriminalForensicPartsGrid().getStore().on({
                'load': {
                    scope: this,
                    fn: function(store, records) {
                        cfg.values.thiswindow.storeFunctionalPerformance(cfg);
                    }
                }
            });
        }
        return this._procForQualAnalysisOfCriminalForensicParts;
    },

    getProcForQualAnalysisOfOutCourtLawsuitProceduresPartsGrid: function(cfg) {
        if(!this._procForQualAnalysisOfOutCourtLawsuitProceduresParts) {
            this._procForQualAnalysisOfOutCourtLawsuitProceduresParts = Ext._create('corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartsoutcourtlawsuit.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 150,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},

            });
            this.getProcForQualAnalysisOfOutCourtLawsuitProceduresPartsGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
            this.getProcForQualAnalysisOfOutCourtLawsuitProceduresPartsGrid().getStore().on({
                'load': {
                    scope: this,
                    fn: function(store, records) {
                        cfg.values.thiswindow.storeFunctionalPerformance(cfg);
                    }
                }
            });
        }
        return this._procForQualAnalysisOfOutCourtLawsuitProceduresParts;
    },

    getProcForQualAnalysisOfElectoralPartsGrid: function(cfg) {
        if(!this._procForQualAnalysisOfElectoralParts) {
            this._procForQualAnalysisOfElectoralParts = Ext._create('corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartselectoral.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 150,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},
            });
            this.getProcForQualAnalysisOfElectoralPartsGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
            this.getProcForQualAnalysisOfElectoralPartsGrid().getStore().on({
                'load': {
                    scope: this,
                    fn: function(store, records) {
                        cfg.values.thiswindow.storeFunctionalPerformance(cfg);
                    }
                }
            });
        }
        return this._procForQualAnalysisOfElectoralParts;
    },

    getQualitativeAnalysisOfCivilForensicPartsForm: function(cfg) {
        if(!this._qualitativeAnalysisOfCivilForensicPartsForm) {
            this._qualitativeAnalysisOfCivilForensicPartsForm = Ext._create('Ext.form.FieldSet', {
                title: '2. Análise Qualitativa das Peças Forenses Cíveis',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                labelWidth: 55,
                width: 1115,
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
                                labelWidth: 85,
                                columnWidth: 0.25,
                                items: [
                                    {
                                        fieldLabel: 'Tem atribuição',
                                        xtype: 'combo',
                                        id: 'qapccl_applicable',
                                        hiddenName: 'qapccl_applicable',
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
                                labelWidth: 85,
                                columnWidth: 0.6,
                                items: [
                                    {
                                        fieldLabel: 'Possui peças?',
                                        xtype: 'combo',
                                        id: 'qapccl_no_parts_to_analyze',
                                        hiddenName: 'qapccl_no_parts_to_analyze',
                                        width: 100,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                        listeners: {
                                            scope: this,
                                            render: function(){
                                                if (Ext.getCmp('qapccl_no_parts_to_analyze').value!=2) {
                                                    this.getProcForQualAnalysisOfCivilForensicPartsGrid(cfg).disable();
                                                } else {
                                                    this.getProcForQualAnalysisOfCivilForensicPartsGrid(cfg).enable();
                                                }
                                            },
                                            select: function(index){
                                                if (index.value!=2) {
                                                    this.getProcForQualAnalysisOfCivilForensicPartsGrid(cfg).disable();
                                                } else {
                                                    this.getProcForQualAnalysisOfCivilForensicPartsGrid(cfg).enable();
                                                }
                                            },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 70,
                                columnWidth: 0.15,
                                items: [
                                    {
                                        xtype: 'displayfield',
                                        id: 'qapccl_score',
                                        name: 'qapccl_score',
                                        fieldLabel: 'Pontuação',
                                        style: {fontWeight: 'bold', fontSize: '14px', },
                                    },
                                ]
                            }
                        ]
                    },
                    this.getProcForQualAnalysisOfCivilForensicPartsGrid(cfg),
                ]
            });
        }
        return this._qualitativeAnalysisOfCivilForensicPartsForm;
    },

    getQualitativeAnalysisOfCriminalForensicPartsForm: function(cfg) {
        if(!this._qualitativeAnalysisOfCriminalForensicPartsForm) {
            this._qualitativeAnalysisOfCriminalForensicPartsForm = Ext._create('Ext.form.FieldSet', {
                title: '3. Análise Qualitativa das Peças Forenses Criminais',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                labelWidth: 55,
                width: 1115,
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
                                labelWidth: 85,
                                columnWidth: 0.25,
                                items: [
                                    {
                                        fieldLabel: 'Tem atribuição',
                                        xtype: 'combo',
                                        id: 'qapcrcl_applicable',
                                        hiddenName: 'qapcrcl_applicable',
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
                                labelWidth: 85,
                                columnWidth: 0.6,
                                items: [
                                    {
                                        fieldLabel: 'Possui peças?',
                                        xtype: 'combo',
                                        id: 'qapcrcl_no_parts_to_analyze',
                                        hiddenName: 'qapcrcl_no_parts_to_analyze',
                                        width: 100,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                        listeners: {
                                            scope: this,
                                            render: function(){
                                                if (Ext.getCmp('qapcrcl_no_parts_to_analyze').value!=2) {
                                                    this.getProcForQualAnalysisOfCriminalForensicPartsGrid(cfg).disable();
                                                } else {
                                                    this.getProcForQualAnalysisOfCriminalForensicPartsGrid(cfg).enable();
                                                }
                                            },
                                            select: function(index){
                                                if (index.value!=2) {
                                                    this.getProcForQualAnalysisOfCriminalForensicPartsGrid(cfg).disable();
                                                } else {
                                                    this.getProcForQualAnalysisOfCriminalForensicPartsGrid(cfg).enable();
                                                }
                                            },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 70,
                                columnWidth: 0.15,
                                items: [
                                    {
                                        xtype: 'displayfield',
                                        id: 'qapcrcl_score',
                                        name: 'qapcrcl_score',
                                        fieldLabel: 'Pontuação',
                                        style: {fontWeight: 'bold', fontSize: '14px', },
                                    },
                                ]
                            }
                        ]
                    },
                    this.getProcForQualAnalysisOfCriminalForensicPartsGrid(cfg)
                ]
            });
        }
        return this._qualitativeAnalysisOfCriminalForensicPartsForm;
    },

    getQualitativeAnalysisOfPartsOfOutCourtLawsuitProceduresForm: function(cfg) {
        if(!this._qualitativeAnalysisOfPartsOfOutCourtLawsuitProceduresForm) {
            this._qualitativeAnalysisOfPartsOfOutCourtLawsuitProceduresForm = Ext._create('Ext.form.FieldSet', {
                title: '4. Análise Qualitativa das Peças dos Procedimentos Extrajudiciais',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                labelWidth: 55,
                width: 1115,
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
                                labelWidth: 85,
                                columnWidth: 0.25,
                                items: [
                                    {
                                        fieldLabel: 'Tem atribuição',
                                        xtype: 'combo',
                                        id: 'qapocl_applicable',
                                        hiddenName: 'qapocl_applicable',
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
                                labelWidth: 85,
                                columnWidth: 0.6,
                                items: [
                                    {
                                        fieldLabel: 'Possui peças?',
                                        xtype: 'combo',
                                        id: 'qapocl_no_parts_to_analyze',
                                        hiddenName: 'qapocl_no_parts_to_analyze',
                                        width: 100,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                        listeners: {
                                            scope: this,
                                            render: function(){
                                                if (Ext.getCmp('qapocl_no_parts_to_analyze').value!=2) {
                                                    this.getProcForQualAnalysisOfOutCourtLawsuitProceduresPartsGrid(cfg).disable();
                                                } else {
                                                    this.getProcForQualAnalysisOfOutCourtLawsuitProceduresPartsGrid(cfg).enable();
                                                }
                                            },
                                            select: function(index){
                                                if (index.value!=2) {
                                                    this.getProcForQualAnalysisOfOutCourtLawsuitProceduresPartsGrid(cfg).disable();
                                                } else {
                                                    this.getProcForQualAnalysisOfOutCourtLawsuitProceduresPartsGrid(cfg).enable();
                                                }
                                            },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 70,
                                columnWidth: 0.15,
                                items: [
                                    {
                                        xtype: 'displayfield',
                                        id: 'qapocl_score',
                                        name: 'qapocl_score',
                                        fieldLabel: 'Pontuação',
                                        style: {fontWeight: 'bold', fontSize: '14px', },
                                    },
                                ]
                            }
                        ]
                    },
                    this.getProcForQualAnalysisOfOutCourtLawsuitProceduresPartsGrid(cfg)
                ]
            });
        }
        return this._qualitativeAnalysisOfPartsOfOutCourtLawsuitProceduresForm;
    },

    getQualitativeAnalysisOfThePartsElectoralForm: function(cfg) {
        if(!this._qualitativeAnalysisOfThePartsElectoralForm) {
            this._qualitativeAnalysisOfThePartsElectoralForm = Ext._create('Ext.form.FieldSet', {
                title: '5. Análise Qualitativa das Peças Eleitorais',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                labelWidth: 55,
                width: 1115,
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
                                labelWidth: 85,
                                columnWidth: 0.25,
                                items: [
                                    {
                                        fieldLabel: 'Tem atribuição',
                                        xtype: 'combo',
                                        id: 'qape_applicable',
                                        hiddenName: 'qape_applicable',
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
                                labelWidth: 85,
                                columnWidth: 0.6,
                                items: [
                                    {
                                        fieldLabel: 'Possui peças?',
                                        xtype: 'combo',
                                        id: 'qape_no_parts_to_analyze',
                                        hiddenName: 'qape_no_parts_to_analyze',
                                        width: 100,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                        listeners: {
                                            scope: this,
                                            render: function(){
                                                if (Ext.getCmp('qape_no_parts_to_analyze').value!=2) {
                                                    this.getProcForQualAnalysisOfElectoralPartsGrid(cfg).disable();
                                                } else {
                                                    this.getProcForQualAnalysisOfElectoralPartsGrid(cfg).enable();
                                                }
                                            },
                                            select: function(index){
                                                if (index.value!=2) {
                                                    this.getProcForQualAnalysisOfElectoralPartsGrid(cfg).disable();
                                                } else {
                                                    this.getProcForQualAnalysisOfElectoralPartsGrid(cfg).enable();
                                                }
                                            },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 70,
                                columnWidth: 0.15,
                                items: [
                                    {
                                        xtype: 'displayfield',
                                        id: 'qape_score',
                                        name: 'qape_score',
                                        fieldLabel: 'Pontuação',
                                        style: {fontWeight: 'bold', fontSize: '14px', },
                                    },
                                ]
                            }
                        ]
                    },
                    this.getProcForQualAnalysisOfElectoralPartsGrid(cfg)
                ]
            });
        }
        return this._qualitativeAnalysisOfThePartsElectoralForm;
    },

    getOperabilityForm: function(cfg) {
        if(!this._operabilityForm) {
            this._operabilityForm = Ext._create('Ext.form.FieldSet', {
                title: 'Operosidade',
                collapsible: true,
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
                                columnWidth: 0.77,
                                items: [
                                    this.getRegisteredPublicAttendanceNumberForm(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.23,
                                items: [
                                    this.getFinalScoreOperabilityForm(cfg),
                                ]
                            },
                        ]
                    },
                    this.getQualitativeAnalysisOfCivilForensicPartsForm(cfg),
                    this.getQualitativeAnalysisOfCriminalForensicPartsForm(cfg),
                    this.getQualitativeAnalysisOfPartsOfOutCourtLawsuitProceduresForm(cfg),
                    this.getQualitativeAnalysisOfThePartsElectoralForm(cfg),
                ]
            });
        }
        return this._operabilityForm;
    },

    getFinalScorePromptnessForm: function(cfg) {
        if(!this._finalScorePromptnessForm) {
            this._finalScorePromptnessForm = Ext._create('Ext.form.FieldSet', {
                title: 'Pontuação Presteza',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                width: 250,
                items:[
                    {
                        xtype: 'displayfield',
                        id: 'promptness_score',
                        name: 'promptness_score',
                        width: '100%',
                        style: {textAlign: 'center', fontSize: '34px', fontWeight: 'bolder'},
                    },
                ]
            });
        }
        return this._finalScorePromptnessForm;
    },

    getPromptnessScore: function(cfg, table, cmp, percentual) {
        this._getPromptnessScore = Ext._create('Ext.data.Store', {
            autoLoad: true,
            proxy: Ext._create('Ext.data.HttpProxy', {
                url: core.callAction('INSPECTIONInspection', 'getPromptnessCalcScore')
            }),
            baseParams: {
                inspection_id: cfg.values.inspection_id,
                table: table,
                percentual: percentual,
            },
            reader: Ext._create('Ext.data.JsonReader', {
                totalProperty: 'count',
                root: 'collection',
                fields: [
                    {type: "auto", name: "score"},
                    {type: "auto", name: "promptness_score"},
                ]
            })
        });
        cache = this._getPromptnessScore;
        this._getPromptnessScore.load({
            'scope': this,
            'callback': function() {
                score = cache.data.items["0"].data.score;
                Ext.getCmp(cmp).setValue(score);
                promptnessscore = cache.data.items["0"].data.promptness_score;
                Ext.getCmp('promptness_score').setValue(promptnessscore);
                // cfg.values.thiswindow.storeFunctionalPerformance(cfg);
            }
        });
    },

    getPromptnessCourtLawsuitForm: function(cfg) {
        if(!this._promptnessCourtLawsuit) {
            this._promptnessCourtLawsuit = Ext._create('Ext.form.FieldSet', {
                title: '1. Cumprimento de prazos processuais nos FEITOS JUDICIAIS (inclusive eleitoral)',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                width: 850,
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
                                columnWidth: 0.65,
                                labelWidth: 65,
                                items: [
                                    {
                                        xtype: 'numberfield',
                                        fieldLabel: 'Percentual',
                                        minValue: 0,
                                        maxValue: 100,
                                        emptyText: 'Informe um valor entre 0.00 e 100.00. Ex.: 55.55',
                                        name: 'pcl_percentual',
                                        hideLabel: false,
                                        width: 300,
                                        listeners: {
                                            scope: this,
                                            change: function(newValue, oldValue ){
                                                this.getPromptnessScore(cfg, 'var_promptness_courtlawsuit', 'pcl_score', oldValue);
                                            },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.35,
                                labelWidth: 65,
                                items: [
                                    {
                                        xtype: 'displayfield',
                                        id: 'pcl_score',
                                        name: 'pcl_score',
                                        width: '100%',
                                        fieldLabel: 'Pontuação',
                                        style: {fontSize: '14px', fontWeight: 'bold'},
                                    },
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._promptnessCourtLawsuit;
    },

    getPromptnessOutCourtLawsuitForm: function(cfg) {
        if(!this._promptnessOutCourtLawsuit) {
            this._promptnessOutCourtLawsuit = Ext._create('Ext.form.FieldSet', {
                title: '2. Cumprimento de prazos nos PROCEDIMENTOS EXTRAJUDICIAIS (inclusive eleitoral)',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                width: 850,
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
                                columnWidth: 0.65,
                                labelWidth: 65,
                                items: [
                                    {
                                        xtype: 'numberfield',
                                        fieldLabel: 'Percentual',
                                        minValue: 0,
                                        maxValue: 100,
                                        emptyText: 'Informe um valor entre 0.00 e 100.00. Ex.: 55.55',
                                        name: 'pocl_percentual',
                                        hideLabel: false,
                                        width: 300,
                                        listeners: {
                                            scope: this,
                                            change: function(newValue, oldValue ){
                                                this.getPromptnessScore(cfg, 'var_promptness_outcourtlawsuit', 'pocl_score', newValue.value);
                                            },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.35,
                                labelWidth: 65,
                                items: [
                                    {
                                        xtype: 'displayfield',
                                        id: 'pocl_score',
                                        name: 'pocl_score',
                                        width: '100%',
                                        fieldLabel: 'Pontuação',
                                        style: {fontSize: '14px', fontWeight: 'bold'},
                                    },
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._promptnessOutCourtLawsuit;
    },

    getPromptnessUpperManagementForm: function(cfg) {
        if(!this._promptnessUpperManagement) {
            this._promptnessUpperManagement = Ext._create('Ext.form.FieldSet', {
                title: '3. Atendimento tempestivo às determinações da Administração Superior e da Ouvidoria',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                width: 850,
                items:[
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        style: {marginBottom: '10px'},
                        items: [
                            {
                                xtype: 'label',
                                text: '(1. Residência  -  2. Docência  -  3.IRPF  -  4. RAF  -  5. Relatórios das Delegacias  -  6. Relatórios das Cadeias  -  7. Relatório de Internação e Semiliberdade  -  8. Relatórios de Acolhimento Familiar  -  9. Comunicações diversas  -  10. Demandas da Ouvidoria)',
                                style: {fontSize: '13px'},
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
                                columnWidth: 0.65,
                                labelWidth: 65,
                                items: [
                                    {
                                        xtype: 'numberfield',
                                        fieldLabel: 'Percentual',
                                        minValue: 0,
                                        maxValue: 100,
                                        emptyText: 'Informe um valor entre 0.00 e 100.00. Ex.: 55.55',
                                        name: 'pum_percentual',
                                        hideLabel: false,
                                        width: 300,
                                        listeners: {
                                            scope: this,
                                            change: function(newValue, oldValue ){
                                                this.getPromptnessScore(cfg, 'var_promptness_uppermanagement', 'pum_score', newValue.value);
                                            },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.35,
                                labelWidth: 65,
                                items: [
                                    {
                                        xtype: 'displayfield',
                                        id: 'pum_score',
                                        name: 'pum_score',
                                        width: '100%',
                                        fieldLabel: 'Pontuação',
                                        style: {fontSize: '14px', fontWeight: 'bold'},
                                    },
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._promptnessUpperManagement;
    },

    getPromptnessForm: function(cfg) {
        if(!this._promptnessForm) {
            this._promptnessForm = Ext._create('Ext.form.FieldSet', {
                title: 'Presteza',
                collapsible: true,
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
                                columnWidth: 0.77,
                                items: [
                                    this.getPromptnessCourtLawsuitForm(cfg),
                                    this.getPromptnessOutCourtLawsuitForm(cfg),
                                    this.getPromptnessUpperManagementForm(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.23,
                                items: [
                                    this.getFinalScorePromptnessForm(cfg),
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._promptnessForm;
    },

    getHarmedCalculationJustification: function(cfg) {
        if(!this._harmedCalculationJustification) {
            this._harmedCalculationJustification = Ext._create('Ext.form.TextArea', {
                fieldLabel: 'Justificativa',
                id: 'hc_justification',
                name: 'hc_justification',
                width: 1035,
                height: 125,
            });
        }
        return this._harmedCalculationJustification;
    },

    getHarmedCalculationForm: function(cfg) {
        if(!this._harmedCalculationForm) {
            this._harmedCalculationForm = Ext._create('Ext.form.FieldSet', {
                title: 'Cálculo Prejudicado',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                items:[
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 115,
                                items: [
                                    {
                                        fieldLabel: 'Cálculo prejudicado?',
                                        xtype: 'combo',
                                        id: 'hc_harmedcalculation',
                                        hiddenName: 'hc_harmedcalculation',
                                        width: 100,
                                        // value: 3,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                        listeners: {
                                            scope: this,
                                            render: function(){
                                                if (Ext.getCmp('hc_harmedcalculation').value!=2) {
                                                    Ext.getCmp('hc_justification').disable();
                                                } else {
                                                    Ext.getCmp('hc_justification').enable();
                                                }
                                            },
                                            select: function(index){
                                                if (index.value!=2) {
                                                    Ext.getCmp('hc_justification').disable();
                                                } else {
                                                    Ext.getCmp('hc_justification').enable();
                                                }
                                            },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 75,
                                items: [
                                    this.getHarmedCalculationJustification(cfg),
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._harmedCalculationForm;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'DO DESEMPENHO FUNCIONAL',
            layout: 'form',
            frame: true,
            height: 575,
            border: false,
            autoScroll: true,
            overflow: 'auto',
            bodyStyle: 'padding: 5px',
            items: [
                this.getOperabilityForm(cfg),
                this.getPromptnessForm(cfg),
                this.getHarmedCalculationForm(cfg),
            ],
        });

        Ext.apply(cfg, {

        });

        corregedoria.inspection.inspection.filling.functionalperformance.Launcher.superclass.constructor.call(this, cfg);

    }
});
