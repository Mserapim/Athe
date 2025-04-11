Ext._define('corregedoria.inspection.inspection.filling.Launcher_executionorgan_prosecution', {
    extend: 'Ext.Window',

    store: function(cfg) {
        if (cfg) {
            if (cfg.values.frame) {
                if (cfg.values.frame == 'regularityofservices') {
                    this.storeRegularityOfService(cfg);
                }
                if (cfg.values.frame == 'structure') {
                    this.storeStructure(cfg);
                }
                if (cfg.values.frame == 'functionalperformance') {
                    this.storeFunctionalPerformance(cfg);
                }
                if (cfg.values.frame == 'generalobservations') {
                    this.storeGeneralObservations(cfg);
                }
                if (cfg.values.frame == 'recommendations') {
                    this.storeRecommendations(cfg);
                }
                if (cfg.values.frame == 'attachments') {
                    this.storeAttachments(cfg);
                }
            } else {
                this.storeRegularityOfService(cfg);
                this.storeStructure(cfg);
                this.storeFunctionalPerformance(cfg);
                this.storeGeneralObservations(cfg);
                this.storeRecommendations(cfg);
                this.storeAttachments(cfg);
            }
        }
    },

    storeRegularityOfService: function(cfg) {
        if(!this._storeRegularityOfService) {
            this._storeRegularityOfService = Ext._create('Ext.data.Store', {
                    // autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONInspection', 'getRegularityOfService')
                    }),
                    baseParams: {
                        inspection_id: cfg.values.inspection_id,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "eom_organization"},
                            {type: "auto", name: "eom_observation"},
                            {type: "auto", name: "pa_record_type"},
                            {type: "auto", name: "pa_apps"},
                            {type: "auto", name: "pa_others"},
                            {type: "auto", name: "pa_opening_date"},
                            {type: "auto", name: "pa_has_openind_term"},
                            {type: "auto", name: "pa_has_numeration"},
                            {type: "auto", name: "pa_has_signed_sheets"},
                            {type: "auto", name: "pa_ordered"},
                            {type: "auto", name: "pa_observation"},
                            {type: "auto", name: "oclsc_record_type"},
                            {type: "auto", name: "oclsc_apps"},
                            {type: "auto", name: "oclsc_others"},
                            {type: "auto", name: "oclsc_opening_date"},
                            {type: "auto", name: "oclsc_has_openind_term"},
                            {type: "auto", name: "oclsc_has_numeration"},
                            {type: "auto", name: "oclsc_has_signed_sheets"},
                            {type: "auto", name: "oclsc_ordered"},
                            {type: "auto", name: "oclsc_observation"},
                            {type: "auto", name: "clsc_record_type"},
                            {type: "auto", name: "clsc_apps"},
                            {type: "auto", name: "clsc_others"},
                            {type: "auto", name: "clsc_opening_date"},
                            {type: "auto", name: "clsc_has_openind_term"},
                            {type: "auto", name: "clsc_has_numeration"},
                            {type: "auto", name: "clsc_has_signed_sheets"},
                            {type: "auto", name: "clsc_ordered"},
                            {type: "auto", name: "clsc_observation"},
                            {type: "auto", name: "clsct_number_of_processes_pending_citation_urgent"},
                            {type: "auto", name: "clsct_number_of_processes_pending_citation"},
                            {type: "auto", name: "clsct_number_of_processes_pending_science"},
                            {type: "auto", name: "clsct_processes_with_open_deadline"},
                            {type: "auto", name: "clsct_expired_deadline_the_last_30_days"},
                            {type: "auto", name: "clsct_expired_deadline_more_than_30_days_ago"},
                            {type: "auto", name: "clsct_expired_deadline_in_the_period_of_inspection"},
                            {type: "auto", name: "clsct_observation"},
                            {type: "auto", name: "oclsect_number_of_procedures_in_progress"},
                            {type: "auto", name: "oclsect_number_of_procedures_in_arrears"},
                            {type: "auto", name: "oclsect_correctly_registered_procedures"},
                            {type: "auto", name: "oclsect_observation"},
                            {type: "auto", name: "oclsct_number_of_procedures_in_progress"},
                            {type: "auto", name: "oclsct_number_of_procedures_in_arrears"},
                            {type: "auto", name: "oclsct_correctly_registered_procedures"},
                            {type: "auto", name: "oclsct_number_of_public_civil_actions_in_the_last_year"},
                            {type: "auto", name: "oclsct_number_of_acp_administrative_dishonesty"},
                            {type: "auto", name: "oclsct_number_of_recommendations_issued_in_the_last_year"},
                            {type: "auto", name: "oclsct_number_of_conduct_adjustment_terms_in_the_last_year"},
                            {type: "auto", name: "oclsct_number_of_public_audiences_in_the_last_year"},
                            {type: "auto", name: "oclsct_number_of_procedures_instituted_in_the_last_year"},
                            {type: "auto", name: "oclsct_number_of_procedures_archived_in_the_last_year"},
                            {type: "auto", name: "oclsct_observation"},
                            {type: "auto", name: "apia_processes_analyzed_in_the_previous_inspection"},
                            {type: "auto", name: "apia_survey_in_randomly_chosen_processes"},
                            {type: "auto", name: "apia_observation"},
                            {type: "auto", name: "apijts_analysis"},
                            {type: "auto", name: "final_score"},
                        ]
                    })
                });
                storeRegularityOfServiceCache = this._storeRegularityOfService;
                this._storeRegularityOfService.load({
                    'scope': this,
                    'callback': function() {
                        this.getFormPanel().getForm().setValues({
                            employee: cfg.values.employee,
                            responsible: cfg.values.responsible,
                            execution_organ: cfg.values.execution_organ,
                            inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,

                            eom_organization: storeRegularityOfServiceCache.data.items["0"].data.eom_organization,
                            eom_observation: storeRegularityOfServiceCache.data.items["0"].data.eom_observation,
                            pa_record_type: storeRegularityOfServiceCache.data.items["0"].data.pa_record_type,
                            pa_apps: storeRegularityOfServiceCache.data.items["0"].data.pa_apps,
                            pa_others: storeRegularityOfServiceCache.data.items["0"].data.pa_others,
                            pa_opening_date: storeRegularityOfServiceCache.data.items["0"].data.pa_opening_date,
                            pa_has_openind_term: storeRegularityOfServiceCache.data.items["0"].data.pa_has_openind_term,
                            pa_has_numeration: storeRegularityOfServiceCache.data.items["0"].data.pa_has_numeration,
                            pa_has_signed_sheets: storeRegularityOfServiceCache.data.items["0"].data.pa_has_signed_sheets,
                            pa_ordered: storeRegularityOfServiceCache.data.items["0"].data.pa_ordered,
                            pa_observation: storeRegularityOfServiceCache.data.items["0"].data.pa_observation,
                            oclsc_record_type: storeRegularityOfServiceCache.data.items["0"].data.oclsc_record_type,
                            oclsc_apps: storeRegularityOfServiceCache.data.items["0"].data.oclsc_apps,
                            oclsc_others: storeRegularityOfServiceCache.data.items["0"].data.oclsc_others,
                            oclsc_opening_date: storeRegularityOfServiceCache.data.items["0"].data.oclsc_opening_date,
                            oclsc_has_openind_term: storeRegularityOfServiceCache.data.items["0"].data.oclsc_has_openind_term,
                            oclsc_has_numeration: storeRegularityOfServiceCache.data.items["0"].data.oclsc_has_numeration,
                            oclsc_has_signed_sheets: storeRegularityOfServiceCache.data.items["0"].data.oclsc_has_signed_sheets,
                            oclsc_ordered: storeRegularityOfServiceCache.data.items["0"].data.oclsc_ordered,
                            oclsc_observation: storeRegularityOfServiceCache.data.items["0"].data.oclsc_observation,
                            clsc_record_type: storeRegularityOfServiceCache.data.items["0"].data.clsc_record_type,
                            clsc_apps: storeRegularityOfServiceCache.data.items["0"].data.clsc_apps,
                            clsc_others: storeRegularityOfServiceCache.data.items["0"].data.clsc_others,
                            clsc_opening_date: storeRegularityOfServiceCache.data.items["0"].data.clsc_opening_date,
                            clsc_has_openind_term: storeRegularityOfServiceCache.data.items["0"].data.clsc_has_openind_term,
                            clsc_has_numeration: storeRegularityOfServiceCache.data.items["0"].data.clsc_has_numeration,
                            clsc_has_signed_sheets: storeRegularityOfServiceCache.data.items["0"].data.clsc_has_signed_sheets,
                            clsc_ordered: storeRegularityOfServiceCache.data.items["0"].data.clsc_ordered,
                            clsc_observation: storeRegularityOfServiceCache.data.items["0"].data.clsc_observation,
                            clsct_number_of_processes_pending_citation_urgent: storeRegularityOfServiceCache.data.items["0"].data.clsct_number_of_processes_pending_citation_urgent,
                            clsct_number_of_processes_pending_citation: storeRegularityOfServiceCache.data.items["0"].data.clsct_number_of_processes_pending_citation,
                            clsct_number_of_processes_pending_science: storeRegularityOfServiceCache.data.items["0"].data.clsct_number_of_processes_pending_science,
                            clsct_processes_with_open_deadline: storeRegularityOfServiceCache.data.items["0"].data.clsct_processes_with_open_deadline,
                            clsct_expired_deadline_the_last_30_days: storeRegularityOfServiceCache.data.items["0"].data.clsct_expired_deadline_the_last_30_days,
                            clsct_expired_deadline_more_than_30_days_ago: storeRegularityOfServiceCache.data.items["0"].data.clsct_expired_deadline_more_than_30_days_ago,
                            clsct_expired_deadline_in_the_period_of_inspection: storeRegularityOfServiceCache.data.items["0"].data.clsct_expired_deadline_in_the_period_of_inspection,
                            clsct_observation: storeRegularityOfServiceCache.data.items["0"].data.clsct_observation,
                            oclsect_number_of_procedures_in_progress: storeRegularityOfServiceCache.data.items["0"].data.oclsect_number_of_procedures_in_progress,
                            oclsect_number_of_procedures_in_arrears: storeRegularityOfServiceCache.data.items["0"].data.oclsect_number_of_procedures_in_arrears,
                            oclsect_correctly_registered_procedures: storeRegularityOfServiceCache.data.items["0"].data.oclsect_correctly_registered_procedures,
                            oclsect_observation: storeRegularityOfServiceCache.data.items["0"].data.oclsect_observation,
                            oclsct_number_of_procedures_in_progress: storeRegularityOfServiceCache.data.items["0"].data.oclsct_number_of_procedures_in_progress,
                            oclsct_number_of_procedures_in_arrears: storeRegularityOfServiceCache.data.items["0"].data.oclsct_number_of_procedures_in_arrears,
                            oclsct_correctly_registered_procedures: storeRegularityOfServiceCache.data.items["0"].data.oclsct_correctly_registered_procedures,
                            oclsct_number_of_public_civil_actions_in_the_last_year: storeRegularityOfServiceCache.data.items["0"].data.oclsct_number_of_public_civil_actions_in_the_last_year,
                            oclsct_number_of_acp_administrative_dishonesty: storeRegularityOfServiceCache.data.items["0"].data.oclsct_number_of_acp_administrative_dishonesty,
                            oclsct_number_of_recommendations_issued_in_the_last_year: storeRegularityOfServiceCache.data.items["0"].data.oclsct_number_of_recommendations_issued_in_the_last_year,
                            oclsct_number_of_conduct_adjustment_terms_in_the_last_year: storeRegularityOfServiceCache.data.items["0"].data.oclsct_number_of_conduct_adjustment_terms_in_the_last_year,
                            oclsct_number_of_public_audiences_in_the_last_year: storeRegularityOfServiceCache.data.items["0"].data.oclsct_number_of_public_audiences_in_the_last_year,
                            oclsct_number_of_procedures_instituted_in_the_last_year: storeRegularityOfServiceCache.data.items["0"].data.oclsct_number_of_procedures_instituted_in_the_last_year,
                            oclsct_number_of_procedures_archived_in_the_last_year: storeRegularityOfServiceCache.data.items["0"].data.oclsct_number_of_procedures_archived_in_the_last_year,
                            oclsct_observation: storeRegularityOfServiceCache.data.items["0"].data.oclsct_observation,
                            apia_processes_analyzed_in_the_previous_inspection: storeRegularityOfServiceCache.data.items["0"].data.apia_processes_analyzed_in_the_previous_inspection,
                            apia_survey_in_randomly_chosen_processes: storeRegularityOfServiceCache.data.items["0"].data.apia_survey_in_randomly_chosen_processes,
                            apia_observation: storeRegularityOfServiceCache.data.items["0"].data.apia_observation,
                            apijts_analysis: storeRegularityOfServiceCache.data.items["0"].data.apijts_analysis,
                            final_score: storeRegularityOfServiceCache.data.items["0"].data.final_score,
                        });
                    }
                });
            }
            return this._storeRegularityOfService;
    },

    getTabRegularityOfService: function(cfg) {
        if(!this._tabRegularityOfService)
            this._tabRegularityOfService = new corregedoria.inspection.inspection.filling.regularityofservices.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                    electoral_applicable: cfg.values.electoral_applicable,
                    thiswindow: this,
                }
            });
        return this._tabRegularityOfService;
    },

    storeStructure: function(cfg) {
        if(!this._storeStructure) {
            this._storeStructure = Ext._create('Ext.data.Store', {
                // autoLoad: true,
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
                        {type: "auto", name: "final_score"},
                    ]
                })
            });
            storeStructureCache = this._storeStructure;
            this._storeStructure.load({
                'scope': this,
                'callback': function() {
                    this.getFormPanel().getForm().setValues({
                        employee: cfg.values.employee,
                        responsible: cfg.values.responsible,
                        execution_organ: cfg.values.execution_organ,
                        inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,

                        est_deficiency: storeStructureCache.data.items["0"].data.est_deficiency,
                        final_score: storeStructureCache.data.items["0"].data.final_score,
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

    storeFunctionalPerformance: function(cfg) {
        this._storeFunctionalPerformance = Ext._create('Ext.data.Store', {
            // id: 'storeFunctionalPerformance',
            // autoLoad: true,
            proxy: Ext._create('Ext.data.HttpProxy', {
                url: core.callAction('INSPECTIONInspection', 'getFunctionalPerformance')
            }),
            baseParams: {
                inspection_id: cfg.values.inspection_id,
            },
            reader: Ext._create('Ext.data.JsonReader', {
                totalProperty: 'count',
                root: 'collection',
                fields: [
                    {type: "auto", name: "operability_score"},
                    {type: "auto", name: "dpl_average"},
                    {type: "auto", name: "dpl_score"},
                    {type: "auto", name: "qapccl_applicable"},
                    {type: "auto", name: "qapccl_no_parts_to_analyze"},
                    {type: "auto", name: "qapccl_score"},
                    {type: "auto", name: "qapcrcl_applicable"},
                    {type: "auto", name: "qapcrcl_no_parts_to_analyze"},
                    {type: "auto", name: "qapcrcl_score"},
                    {type: "auto", name: "qapocl_applicable"},
                    {type: "auto", name: "qapocl_no_parts_to_analyze"},
                    {type: "auto", name: "qapocl_score"},
                    {type: "auto", name: "qape_applicable"},
                    {type: "auto", name: "qape_no_parts_to_analyze"},
                    {type: "auto", name: "qape_score"},
                    {type: "auto", name: "promptness_score"},
                    {type: "auto", name: "pcl_percentual"},
                    {type: "auto", name: "pcl_score"},
                    {type: "auto", name: "pocl_percentual"},
                    {type: "auto", name: "pocl_score"},
                    {type: "auto", name: "pum_percentual"},
                    {type: "auto", name: "pum_score"},
                    {type: "auto", name: "final_score"},
                    {type: "auto", name: "hc_harmedcalculation"},
                    {type: "auto", name: "hc_justification"},
                ]
            })
        });
        storeFunctionalPerformanceCache = this._storeFunctionalPerformance;
        this._storeFunctionalPerformance.load({
            'scope': this,
            'callback': function() {
                if (storeFunctionalPerformanceCache.data.items["0"]) {
                    this.getFormPanel().getForm().setValues({
                        operability_score: storeFunctionalPerformanceCache.data.items["0"].data.operability_score,
                        dpl_average: storeFunctionalPerformanceCache.data.items["0"].data.dpl_average,
                        dpl_score: storeFunctionalPerformanceCache.data.items["0"].data.dpl_score,
                        qapccl_applicable: storeFunctionalPerformanceCache.data.items["0"].data.qapccl_applicable,
                        qapccl_no_parts_to_analyze: storeFunctionalPerformanceCache.data.items["0"].data.qapccl_no_parts_to_analyze,
                        qapccl_score: storeFunctionalPerformanceCache.data.items["0"].data.qapccl_score,
                        qapcrcl_applicable: storeFunctionalPerformanceCache.data.items["0"].data.qapcrcl_applicable,
                        qapcrcl_no_parts_to_analyze: storeFunctionalPerformanceCache.data.items["0"].data.qapcrcl_no_parts_to_analyze,
                        qapcrcl_score: storeFunctionalPerformanceCache.data.items["0"].data.qapcrcl_score,
                        qapocl_applicable: storeFunctionalPerformanceCache.data.items["0"].data.qapocl_applicable,
                        qapocl_no_parts_to_analyze: storeFunctionalPerformanceCache.data.items["0"].data.qapocl_no_parts_to_analyze,
                        qapocl_score: storeFunctionalPerformanceCache.data.items["0"].data.qapocl_score,
                        qape_applicable: storeFunctionalPerformanceCache.data.items["0"].data.qape_applicable,
                        qape_no_parts_to_analyze: storeFunctionalPerformanceCache.data.items["0"].data.qape_no_parts_to_analyze,
                        qape_score: storeFunctionalPerformanceCache.data.items["0"].data.qape_score,
                        promptness_score: storeFunctionalPerformanceCache.data.items["0"].data.promptness_score,
                        pcl_percentual: storeFunctionalPerformanceCache.data.items["0"].data.pcl_percentual,
                        pcl_score: storeFunctionalPerformanceCache.data.items["0"].data.pcl_score,
                        pocl_percentual: storeFunctionalPerformanceCache.data.items["0"].data.pocl_percentual,
                        pocl_score: storeFunctionalPerformanceCache.data.items["0"].data.pocl_score,
                        pum_percentual: storeFunctionalPerformanceCache.data.items["0"].data.pum_percentual,
                        pum_score: storeFunctionalPerformanceCache.data.items["0"].data.pum_score,
                        final_score: storeFunctionalPerformanceCache.data.items["0"].data.final_score,
                        hc_harmedcalculation: storeFunctionalPerformanceCache.data.items["0"].data.hc_harmedcalculation,
                        hc_justification: storeFunctionalPerformanceCache.data.items["0"].data.hc_justification,
                    });
                    if (storeFunctionalPerformanceCache.data.items["0"].data.qapccl_no_parts_to_analyze == 2) {
                        this.getTabFunctionalPerformance(cfg).getProcForQualAnalysisOfCivilForensicPartsGrid(cfg).enable();
                    }
                    if (storeFunctionalPerformanceCache.data.items["0"].data.qapcrcl_no_parts_to_analyze == 2) {
                        this.getTabFunctionalPerformance(cfg).getProcForQualAnalysisOfCriminalForensicPartsGrid(cfg).enable();
                    }
                    if (storeFunctionalPerformanceCache.data.items["0"].data.qapocl_no_parts_to_analyze == 2) {
                        this.getTabFunctionalPerformance(cfg).getProcForQualAnalysisOfOutCourtLawsuitProceduresPartsGrid(cfg).enable();
                    }
                    if (storeFunctionalPerformanceCache.data.items["0"].data.qape_no_parts_to_analyze == 2) {
                        this.getTabFunctionalPerformance(cfg).getProcForQualAnalysisOfElectoralPartsGrid(cfg).enable();
                    }
                    if (storeFunctionalPerformanceCache.data.items["0"].data.qape_no_parts_to_analyze == 2) {
                        this.getTabFunctionalPerformance(cfg).getProcForQualAnalysisOfElectoralPartsGrid(cfg).enable();
                    }
                    if (storeFunctionalPerformanceCache.data.items["0"].data.hc_harmedcalculation == 2) {
                        this.getTabFunctionalPerformance(cfg).getHarmedCalculationJustification(cfg).enable();
                    }
                }
            }
        });
        return this._storeFunctionalPerformance;
    },

    getTabFunctionalPerformance: function(cfg) {
        if(!this._functionalPerformance)
            this._functionalPerformance = new corregedoria.inspection.inspection.filling.functionalperformance.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                    thiswindow: this,
                    final_score: Ext.getCmp('final_score'),
                }
            });
        return this._functionalPerformance;
    },

    storeGeneralObservations: function(cfg) {
        if(!this._storeGeneralObservations) {
            this._storeGeneralObservations = Ext._create('Ext.data.Store', {
                    // autoLoad: true,
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
                            {type: "auto", name: "final_score"},
                        ]
                    })
                });
                storeGeneralObservationsCache = this._storeGeneralObservations;
                this._storeGeneralObservations.load({
                    scope: this,
                    callback: function() {
                        this.getFormPanel().getForm().setValues({
                            employee: cfg.values.employee,
                            responsible: cfg.values.responsible,
                            execution_organ: cfg.values.execution_organ,
                            inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,

                            go_generalobservations: storeGeneralObservationsCache.data.items["0"].data.go_generalobservations,
                            final_score: storeGeneralObservationsCache.data.items["0"].data.final_score,
                        });
                    }
                });
            }
            return this._storeGeneralObservations;
    },

    getTabGeneralObservations: function(cfg) {
        if(!this._generalObservations) {
            this._generalObservations = new corregedoria.inspection.inspection.filling.generalobservations.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                }
            });
        }
        return this._generalObservations;
    },

    storeRecommendations: function(cfg) {
        if(!this._storeRecommendations) {
            this._storeRecommendations = Ext._create('Ext.data.Store', {
                    // autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONInspection', 'getRecommendations')
                    }),
                    baseParams: {
                        inspection_id: cfg.values.inspection_id,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "final_score"},
                        ]
                    })
                });
                storeRecommendationsCache = this._storeRecommendations;
                this._storeRecommendations.load({
                    scope: this,
                    callback: function() {
                        this.getFormPanel().getForm().setValues({
                            employee: cfg.values.employee,
                            responsible: cfg.values.responsible,
                            execution_organ: cfg.values.execution_organ,
                            inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,

                            final_score: storeRecommendationsCache.data.items["0"].data.final_score,
                        });
                    }
                });
            }
            return this._storeRecommendations;
    },

    getTabRecommendations: function(cfg) {
        if(!this._recommendations)
            this._recommendations = new corregedoria.inspection.inspection.filling.recommendations.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                }
            });
        return this._recommendations;
    },

    storeAttachments: function(cfg) {
        if(!this._storeAttachments) {
            this._storeAttachments = Ext._create('Ext.data.Store', {
                    // autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONInspection', 'getAttachments')
                    }),
                    baseParams: {
                        inspection_id: cfg.values.inspection_id,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "final_score"},
                        ]
                    })
                });
                storeAttachmentsCache = this._storeAttachments;
                this._storeAttachments.load({
                    scope: this,
                    callback: function() {
                        this.getFormPanel().getForm().setValues({
                            employee: cfg.values.employee,
                            responsible: cfg.values.responsible,
                            execution_organ: cfg.values.execution_organ,
                            inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,

                            final_score: storeAttachmentsCache.data.items["0"].data.final_score,
                        });
                    }
                });
            }
            return this._storeAttachments;
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
            if (cfg.values.frame == 'regularityofservices') {
                ret = [ this.getTabRegularityOfService(cfg) ];
            }
            if (cfg.values.frame == 'structure') {
                ret = [ this.getTabStructure(cfg) ];
            }
            if (cfg.values.frame == 'functionalperformance') {
                ret = [ this.getTabFunctionalPerformance(cfg) ];
            }
            if (cfg.values.frame == 'generalobservations') {
                ret = [ this.getTabGeneralObservations(cfg) ];
            }
            if (cfg.values.frame == 'recommendations') {
                ret = [ this.getTabRecommendations(cfg) ];
            }
            if (cfg.values.frame == 'attachments') {
                ret = [ this.getTabAttachments(cfg) ];
            }
        } else {
            ret = [
                this.getTabRegularityOfService(cfg),
                this.getTabStructure(cfg),
                this.getTabFunctionalPerformance(cfg),
                this.getTabGeneralObservations(cfg),
                this.getTabRecommendations(cfg),
                this.getTabAttachments(cfg),
             ];
        }
        return ret;
    },

    getFinalScoreForm: function(cfg) {
        if(!this._finalScoreForm) {
            this._finalScoreForm = Ext._create('Ext.form.FieldSet', {
                title: 'Nota Final',
                collapsible: false,
                collapsed: false,
                autoHeight:true,
                width: 250,
                labelWidth: 1,
                items:[
                    {
                        xtype: 'displayfield',
                        id: 'final_score',
                        name: 'final_score',
                        style: {textAlign: 'center', fontSize: '56px', fontWeight: 'bolder'},
                    },
                ]
            });
        }
        return this._finalScoreForm;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            if (cfg) {
                this._formPanel = Ext._create('Ext.form.FormPanel', {
                    border: false,
                    frame: true,
                    // id: 'formPanel',
                    items: [
                        {
                            xtype:'panel',
                            autoHeight:true,
                            layout: 'form',
                            labelWidth: 125,
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
                                            columnWidth: 0.78,
                                            items: [
                                                {
                                                    xtype:'fieldset',
                                                    title: 'Inspeção/Correição',
                                                    collapsible: false,
                                                    collapsed: false,
                                                    autoHeight:true,
                                                    width: 905,
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
                                                                    width: 1000,
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
                                                                    width: 1000,
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
                                                                    width: 1000,
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
                                                                    width: 1000,
                                                                    style: {fontWeight: 'bold'},
                                                                },
                                                            ]
                                                        },
                                                    ]
                                                },
                                            ]
                                        },
                                        {
                                            xtype:'panel',
                                            autoHeight:true,
                                            layout: 'form',
                                            columnWidth: 0.22,
                                            height: 250,
                                            items: [
                                                this.getFinalScoreForm(cfg),
                                            ]
                                        },
                                    ]
                                },
                            ]
                        },
                        {
                            xtype:'tabpanel',
                            // id: 'tabpanel_frames',
                            activeTab: 0,
                            height: 580,
                            border: false,
                            items: [
                                this.getFrames(cfg),
                            ],
                        },
                    ]
                });
        } else {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                // id: 'formPanel',
                items: [ ]
            });
        }
        return this._formPanel;
    },

    getFieldsRegularityOfServices: function(values) {
        ret = {
            eom_organization: values.eom_organization,
            eom_observation: values.eom_observation,
            pa_record_type: values.pa_record_type,
            pa_apps: values.pa_apps,
            pa_others: values.pa_others,
            pa_opening_date: values.pa_opening_date,
            pa_has_openind_term: values.pa_has_openind_term,
            pa_has_numeration: values.pa_has_numeration,
            pa_has_signed_sheets: values.pa_has_signed_sheets,
            pa_ordered: values.pa_ordered,
            pa_observation: values.pa_observation,
            oclsc_record_type: values.oclsc_record_type,
            oclsc_apps: values.oclsc_apps,
            oclsc_others: values.oclsc_others,
            oclsc_opening_date: values.oclsc_opening_date,
            oclsc_has_openind_term: values.oclsc_has_openind_term,
            oclsc_has_numeration: values.oclsc_has_numeration,
            oclsc_has_signed_sheets: values.oclsc_has_signed_sheets,
            oclsc_ordered: values.oclsc_ordered,
            oclsc_observation: values.oclsc_observation,
            clsc_record_type: values.clsc_record_type,
            clsc_apps: values.clsc_apps,
            clsc_others: values.clsc_others,
            clsc_opening_date: values.clsc_opening_date,
            clsc_has_openind_term: values.clsc_has_openind_term,
            clsc_has_numeration: values.clsc_has_numeration,
            clsc_has_signed_sheets: values.clsc_has_signed_sheets,
            clsc_ordered: values.clsc_ordered,
            clsc_observation: values.clsc_observation,
            clsct_number_of_processes_pending_citation_urgent: values.clsct_number_of_processes_pending_citation_urgent,
            clsct_number_of_processes_pending_citation: values.clsct_number_of_processes_pending_citation,
            clsct_number_of_processes_pending_science: values.clsct_number_of_processes_pending_science,
            clsct_processes_with_open_deadline: values.clsct_processes_with_open_deadline,
            clsct_expired_deadline_the_last_30_days: values.clsct_expired_deadline_the_last_30_days,
            clsct_expired_deadline_more_than_30_days_ago: values.clsct_expired_deadline_more_than_30_days_ago,
            clsct_expired_deadline_in_the_period_of_inspection: values.clsct_expired_deadline_in_the_period_of_inspection,
            clsct_observation: values.clsct_observation,
            oclsect_number_of_procedures_in_progress: values.oclsect_number_of_procedures_in_progress,
            oclsect_number_of_procedures_in_arrears: values.oclsect_number_of_procedures_in_arrears,
            oclsect_correctly_registered_procedures: values.oclsect_correctly_registered_procedures,
            oclsect_observation: values.oclsect_observation,
            oclsct_number_of_procedures_in_progress: values.oclsct_number_of_procedures_in_progress,
            oclsct_number_of_procedures_in_arrears: values.oclsct_number_of_procedures_in_arrears,
            oclsct_correctly_registered_procedures: values.oclsct_correctly_registered_procedures,
            oclsct_number_of_public_civil_actions_in_the_last_year: values.oclsct_number_of_public_civil_actions_in_the_last_year,
            oclsct_number_of_acp_administrative_dishonesty: values.oclsct_number_of_acp_administrative_dishonesty,
            oclsct_number_of_recommendations_issued_in_the_last_year: values.oclsct_number_of_recommendations_issued_in_the_last_year,
            oclsct_number_of_conduct_adjustment_terms_in_the_last_year: values.oclsct_number_of_conduct_adjustment_terms_in_the_last_year,
            oclsct_number_of_public_audiences_in_the_last_year: values.oclsct_number_of_public_audiences_in_the_last_year,
            oclsct_number_of_procedures_instituted_in_the_last_year: values.oclsct_number_of_procedures_instituted_in_the_last_year,
            oclsct_number_of_procedures_archived_in_the_last_year: values.oclsct_number_of_procedures_archived_in_the_last_year,
            oclsct_observation: values.oclsct_observation,
            apia_processes_analyzed_in_the_previous_inspection: values.apia_processes_analyzed_in_the_previous_inspection,
            apia_survey_in_randomly_chosen_processes: values.apia_survey_in_randomly_chosen_processes,
            apia_observation: values.apia_observation,
            apijts_analysis: values.apijts_analysis
        };
        return ret;
    },

    getFieldsStructure: function(values) {
        ret = {
            est_deficiency: values.est_deficiency
        };
        return ret;
    },

    getFieldsFunctionalPerformance: function(values) {
        ret = {
            qapccl_applicable: values.qapccl_applicable,
            qapccl_no_parts_to_analyze: values.qapccl_no_parts_to_analyze,
            qapcrcl_applicable: values.qapcrcl_applicable,
            qapcrcl_no_parts_to_analyze: values.qapcrcl_no_parts_to_analyze,
            qapocl_applicable: values.qapocl_applicable,
            qapocl_no_parts_to_analyze: values.qapocl_no_parts_to_analyze,
            qape_applicable: values.qape_applicable,
            qape_no_parts_to_analyze: values.qape_no_parts_to_analyze,
            hc_harmedcalculation: values.hc_harmedcalculation,
            hc_justification: values.hc_justification,
        };
        return ret;
    },

    getFieldsGeneralObservations: function(values) {
        ret = {
            go_generalobservations: values.go_generalobservations,
        };
        return ret;
    },

    getFieldsRecommendations: function(values) {
        ret = {

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
            if (cfg.values.frame == 'regularityofservices') {
                ret = Object.assign(save, this.getFieldsRegularityOfServices(values) );
            }
            if (cfg.values.frame == 'structure') {
                ret = Object.assign(save, this.getFieldsStructure(values));
            }
            if (cfg.values.frame == 'functionalperformance') {
                ret = Object.assign(save, this.getFieldsFunctionalPerformance(values));
            }
            if (cfg.values.frame == 'generalobservations') {
                ret = Object.assign(save, this.getFieldsGeneralObservations(values));
            }
            if (cfg.values.frame == 'recommendations') {
                ret = Object.assign(save, this.getFieldsRecommendations(values));
            }
            if (cfg.values.frame == 'attachments') {
                ret = Object.assign(save, this.getFieldsAttachments(values));
            }
        } else {
            ret = Object.assign(save, this.getFieldsRegularityOfServices(values), this.getFieldsStructure(values), this.getFieldsFunctionalPerformance(values), this.getFieldsGeneralObservations(values), this.getFieldsRecommendations(values), this.getFieldsAttachments(values) );
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
                            this.storeFunctionalPerformance(cfg);
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.gridInspection.getStore().reload();
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
        corregedoria.inspection.inspection.filling.Launcher_executionorgan_prosecution.superclass.constructor.call(this, cfg);
        if (cfg) {
            this.getFormPanel().getForm().setValues({
                employee: cfg.values.employee,
                responsible: cfg.values.responsible,
                execution_organ: cfg.values.execution_organ,
                inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final
            });
            this.store(cfg);
        }
    }
});
