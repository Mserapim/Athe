Ext._define('corregedoria.inspection.inspection.filling.Launcher_auxiliaryorgan', {
    extend: 'Ext.Window',

    store: function(cfg) {
        if (cfg) {
            if (cfg.values.frame) {
                if (cfg.values.frame == 'generaldata') {
                    this.storeGeneralData(cfg);
                }
                if (cfg.values.frame == 'operatingstructure') {
                    this.storeOperatingStructure(cfg);
                }
                if (cfg.values.frame == 'administrativeorganization') {
                    this.storeAdministrativeOrganization(cfg);
                }
                if (cfg.values.frame == 'performance') {
                    this.storePerformance(cfg);
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
                this.storeGeneralData(cfg);
                this.storeOperatingStructure(cfg);
                this.storeAdministrativeOrganization(cfg);
                this.storePerformance(cfg);
                this.storeGeneralObservations(cfg);
                this.storeRecommendations(cfg);
                this.storeAttachments(cfg);
            }
        }
    },

    storeGeneralData: function(cfg) {
        if(!this._storeGeneralData) {
            this._storeGeneralData = Ext._create('Ext.data.Store', {
                    // autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONInspection', 'getGeneralData')
                    }),
                    baseParams: {
                        inspection_id: cfg.values.inspection_id,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [

                        ]
                    })
                });
                storeGeneralDataCache = this._storeGeneralData;
                this._storeGeneralData.load({
                    scope: this,
                    callback: function() {
                        this.getFormPanel(cfg).getForm().setValues({

                        });
                    }
                });
            }
            return this._storeGeneralData;
    },

    getTabGeneralData: function(cfg) {
        if(!this._generalData) {
            this._generalData = new corregedoria.inspection.inspection.filling.generaldata.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                }
            });
        }
        return this._generalData;
    },

    storeOperatingStructure: function(cfg) {
        if(!this._storeOperatingStructure) {
            this._storeOperatingStructure = Ext._create('Ext.data.Store', {
                    // autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONInspection', 'getOperatingStructure')
                    }),
                    baseParams: {
                        inspection_id: cfg.values.inspection_id,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "os_location"},
                            {type: "auto", name: "os_deficiency"},
                            {type: "auto", name: "os_structuregeneralstatus"},
                        ]
                    })
                });
                storeOperatingStructureCache = this._storeOperatingStructure;
                this._storeOperatingStructure.load({
                    scope: this,
                    callback: function() {
                        this.getFormPanel(cfg).getForm().setValues({
                            os_location: storeOperatingStructureCache.data.items["0"].data.os_location,
                            os_deficiency: storeOperatingStructureCache.data.items["0"].data.os_deficiency,
                            os_structuregeneralstatus: storeOperatingStructureCache.data.items["0"].data.os_structuregeneralstatus,
                        });
                    }
                });
            }
            return this._storeOperatingStructure;
    },

    getTabOperatingStructure: function(cfg) {
        if(!this._operatingStructure) {
            this._operatingStructure = new corregedoria.inspection.inspection.filling.operatingstructure.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                    var_structuregeneralstatus: cfg.values.var_structuregeneralstatus,
                }
            });
        }
        return this._operatingStructure;
    },

    storeAdministrativeOrganization: function(cfg) {
        if(!this._storeAdministrativeOrganization) {
            this._storeAdministrativeOrganization = Ext._create('Ext.data.Store', {
                    // autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONInspection', 'getAdministrativeOrganization')
                    }),
                    baseParams: {
                        inspection_id: cfg.values.inspection_id,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "ao_administrativeorganizationgeneralstatus"},
                            {type: "auto", name: "ao_operate_schedule1_initial"},
                            {type: "auto", name: "ao_operate_schedule1_final"},
                            {type: "auto", name: "ao_operate_schedule2_initial"},
                            {type: "auto", name: "ao_operate_schedule2_final"},
                            {type: "auto", name: "aooh_observation"},
                            {type: "bool", name: "daily_attendance"},
                            {type: "auto", name: "days_of_attendance_per_week"},
                            {type: "auto", name: "ao_attendance_schedule1_initial"},
                            {type: "auto", name: "ao_attendance_schedule1_final"},
                            {type: "auto", name: "ao_attendance_schedule2_initial"},
                            {type: "auto", name: "ao_attendance_schedule2_final"},
                            {type: "auto", name: "aoah_observation"},
                            {type: "auto", name: "ao_registration_type"},
                            {type: "auto", name: "aors_observation"},

                        ]
                    })
                });
                storeAdministrativeOrganizationCache = this._storeAdministrativeOrganization;
                this._storeAdministrativeOrganization.load({
                    scope: this,
                    callback: function() {
                        this.getFormPanel(cfg).getForm().setValues({
                            ao_administrativeorganizationgeneralstatus: storeAdministrativeOrganizationCache.data.items["0"].data.ao_administrativeorganizationgeneralstatus,
                            ao_operate_schedule1_initial: storeAdministrativeOrganizationCache.data.items["0"].data.ao_operate_schedule1_initial,
                            ao_operate_schedule1_final: storeAdministrativeOrganizationCache.data.items["0"].data.ao_operate_schedule1_final,
                            ao_operate_schedule2_initial: storeAdministrativeOrganizationCache.data.items["0"].data.ao_operate_schedule2_initial,
                            ao_operate_schedule2_final: storeAdministrativeOrganizationCache.data.items["0"].data.ao_operate_schedule2_final,
                            aooh_observation: storeAdministrativeOrganizationCache.data.items["0"].data.aooh_observation,
                            daily_attendance: storeAdministrativeOrganizationCache.data.items["0"].data.daily_attendance,
                            days_of_attendance_per_week: storeAdministrativeOrganizationCache.data.items["0"].data.days_of_attendance_per_week,
                            ao_attendance_schedule1_initial: storeAdministrativeOrganizationCache.data.items["0"].data.ao_attendance_schedule1_initial,
                            ao_attendance_schedule1_final: storeAdministrativeOrganizationCache.data.items["0"].data.ao_attendance_schedule1_final,
                            ao_attendance_schedule2_initial: storeAdministrativeOrganizationCache.data.items["0"].data.ao_attendance_schedule2_initial,
                            ao_attendance_schedule2_final: storeAdministrativeOrganizationCache.data.items["0"].data.ao_attendance_schedule2_final,
                            aoah_observation: storeAdministrativeOrganizationCache.data.items["0"].data.aoah_observation,
                            ao_registration_type: storeAdministrativeOrganizationCache.data.items["0"].data.ao_registration_type,
                            aors_observation: storeAdministrativeOrganizationCache.data.items["0"].data.aors_observation,
                        });
                    }
                });
            }
            return this._storeAdministrativeOrganization;
    },

    getTabAdministrativeOrganization: function(cfg) {
        if(!this._administrativeOrganization) {
            this._administrativeOrganization = new corregedoria.inspection.inspection.filling.administrativeorganization.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                    var_administrativeorganizationgeneralstatus: cfg.values.var_administrativeorganizationgeneralstatus,
                    var_registration_type: cfg.values.var_registration_type,
                }
            });
        }
        return this._administrativeOrganization;
    },

    storePerformance: function(cfg) {
        if(!this._storePerformance) {
            this._storePerformance = Ext._create('Ext.data.Store', {
                    // autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONInspection', 'getPerformance')
                    }),
                    baseParams: {
                        inspection_id: cfg.values.inspection_id,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "prf_performance"},
                        ]
                    })
                });
                storePerformanceCache = this._storePerformance;
                this._storePerformance.load({
                    scope: this,
                    callback: function() {
                        this.getFormPanel(cfg).getForm().setValues({
                            prf_performance: storePerformanceCache.data.items["0"].data.prf_performance,
                        });
                    }
                });
            }
            return this._storePerformance;
    },

    getTabPerformance: function(cfg) {
        if(!this._performance) {
            this._performance = new corregedoria.inspection.inspection.filling.performance.Launcher({
                values: {
                    inspection_id: cfg.values.inspection_id,
                }
            });
        }
        return this._performance;
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
                        this.getFormPanel(cfg).getForm().setValues({
                            // employee: cfg.values.employee,
                            // responsible: cfg.values.responsible,
                            // execution_organ: cfg.values.execution_organ,
                            // inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,

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
                        this.getFormPanel(cfg).getForm().setValues({
                            // employee: cfg.values.employee,
                            // responsible: cfg.values.responsible,
                            // execution_organ: cfg.values.execution_organ,
                            // inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,

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
                        this.getFormPanel(cfg).getForm().setValues({
                            // employee: cfg.values.employee,
                            // responsible: cfg.values.responsible,
                            // execution_organ: cfg.values.execution_organ,
                            // inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,

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
            if (cfg.values.frame == 'generaldata') {
                ret = [ this.getTabGeneralData(cfg) ];
            }
            if (cfg.values.frame == 'operatingstructure') {
                ret = [ this.getTabOperatingStructure(cfg) ];
            }
            if (cfg.values.frame == 'administrativeorganization') {
                ret = [ this.getTabAdministrativeOrganization(cfg) ];
            }
            if (cfg.values.frame == 'performance') {
                ret = [ this.getTabPerformance(cfg) ];
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
                this.getTabGeneralData(cfg),
                this.getTabOperatingStructure(cfg),
                this.getTabAdministrativeOrganization(cfg),
                this.getTabPerformance(cfg),
                this.getTabGeneralObservations(cfg),
                this.getTabRecommendations(cfg),
                this.getTabAttachments(cfg),
             ];
        }
        return ret;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            if (cfg) {
                this._formPanel = Ext._create('Ext.form.FormPanel', {
                    border: false,
                    // standardSubmit: true,
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
                                            labelWidth: 85,
                                            items: [
                                                {
                                                    xtype: 'displayfield',
                                                    name: 'execution_organ',
                                                    fieldLabel: 'Grupo Especial',
                                                    width: 1000,
                                                    style: {fontWeight: 'bold'},
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
                                                    name: 'inspector_general',
                                                    fieldLabel: 'Procurador-Geral',
                                                    width: 1000,
                                                    style: {fontWeight: 'bold'},
                                                },
                                            ]
                                        },
                                        {
                                            xtype:'panel',
                                            autoHeight:true,
                                            layout: 'form',
                                            labelWidth: 125,
                                            items: [
                                                {
                                                    xtype: 'displayfield',
                                                    name: 'inspector_prosecutor',
                                                    fieldLabel: 'Promotor-Corregedor',
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
                            xtype:'tabpanel',
                            id: 'tabpanel_frames',
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

    getFieldsGeneralData: function(values) {
        ret = {

        };
        return ret;
    },

    getFieldsOperatingStructure: function(values) {
        ret = {
            os_location: values.os_location,
            os_deficiency: values.os_deficiency,
            os_structuregeneralstatus: values.os_structuregeneralstatus,
        };
        return ret;
    },

    getFieldsAdministrativeOrganization: function(values) {
        ret = {
            ao_administrativeorganizationgeneralstatus: values.ao_administrativeorganizationgeneralstatus,
            ao_operate_schedule1_initial: values.ao_operate_schedule1_initial,
            ao_operate_schedule1_final: values.ao_operate_schedule1_final,
            ao_operate_schedule2_initial: values.ao_operate_schedule2_initial,
            ao_operate_schedule2_final: values.ao_operate_schedule2_final,
            aooh_observation: values.aooh_observation,
            daily_attendance: values.daily_attendance,
            days_of_attendance_per_week: values.days_of_attendance_per_week,
            ao_attendance_schedule1_initial: values.ao_attendance_schedule1_initial,
            ao_attendance_schedule1_final: values.ao_attendance_schedule1_final,
            ao_attendance_schedule2_initial: values.ao_attendance_schedule2_initial,
            ao_attendance_schedule2_final: values.ao_attendance_schedule2_final,
            aoah_observation: values.aoah_observation,
            ao_registration_type: values.ao_registration_type,
            aors_observation: values.aors_observation,
        };
        return ret;
    },

    getFieldsPerformance: function(values) {
        ret = {
            prf_performance: values.prf_performance,
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
            if (cfg.values.frame == 'generaldata') {
                ret = Object.assign(save, this.getFieldsGeneralData(values));
            }
            if (cfg.values.frame == 'operatingstructure') {
                ret = Object.assign(save, this.getFieldsOperatingStructure(values));
            }
            if (cfg.values.frame == 'administrativeorganization') {
                ret = Object.assign(save, this.getFieldsAdministrativeOrganization(values));
            }
            if (cfg.values.frame == 'performance') {
                ret = Object.assign(save, this.getFieldsPerformance(values));
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
            ret = Object.assign(save, this.getFieldsGeneralData(values), this.getFieldsOperatingStructure(values), this.getFieldsAdministrativeOrganization(values), this.getFieldsPerformance(values), this.getFieldsGeneralObservations(values), this.getFieldsRecommendations(values), this.getFieldsAttachments(values) );
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
                            // cfg.values.gridInspection.getStore().reload();
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
            title: 'Gestor de Inspeções/Correições - ÓRGÃOS AUXILIARES',
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
        corregedoria.inspection.inspection.filling.Launcher_auxiliaryorgan.superclass.constructor.call(this, cfg);
        if (cfg) {
            this.getFormPanel(cfg).getForm().setValues({
                inspector_general: cfg.values.inspector_general,
                inspector_prosecutor: cfg.values.inspector_prosecutor,
                execution_organ: cfg.values.execution_organ,
                inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final
            });
            this.store(cfg);
        }
    }
});
