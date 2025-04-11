
Ext._define('corregedoria.inspection.inspection.filling.regularityofservices.Launcher', {
    extend: 'Ext.Panel',

    getExecutionOrganManagementForm: function(cfg) {
        if(!this._executionOrganManagementForm) {
            this._executionOrganManagementForm = Ext._create('Ext.form.FieldSet', {
                title: '1. Gestão da Promotoria',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
                items:[
                    {
                        xtype: 'choicefield',
                        fieldLabel: '1.1 Organização de documentos/expedientes recebidos e expedidos; organização dos materiais de expediente; organização dos livros obrigatórios; organização e controle dos procedimentos extrajudiciais; organização do arquivo',
                        hiddenName: 'eom_organization',
                        width: 150,
                        choiceId: 'inspection.ORGANIZATION',
                        value: 1,
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 80,
                        style: {
                            marginLeft: '520px',
                        },
                        items: [
                            {
                                fieldLabel: 'Observações',
                                xtype: 'textarea',
                                name: 'eom_observation',
                                width: 500,
                                height: 125,
                            }
                        ]
                    },
                ]
            });
        }
        return this._executionOrganManagementForm;
    },

    getRegistrationPublicAttendanceGrid: function(cfg) {
        if(!this._processGrid) {
            this._processGrid = Ext._create('corregedoria.inspection.inspection.filling.regularityofservices.registrationpublicattendance.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 135,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
            });
            this.getRegistrationPublicAttendanceGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
            // this.getRegistrationPublicAttendanceGrid().getStore().on({
            //     'load': {
            //         scope: this,
            //         fn: function(records, options) {
            //             cfg.values.thiswindow.storeFunctionalPerformance(cfg);
            //         },
            //     },
            // });
        }
        return this._processGrid;
    },

    getPublicAttendanceForm: function(cfg) {
        if(!this._publicAttendanceForm) {
            this._publicAttendanceForm = Ext._create('Ext.form.FieldSet', {
                title: '2. Atendimento ao Público',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
                defaults: {
                    labelAlign: 'left',
                },
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
                                labelWidth: 220,
                                columnWidth: 0.45,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: '2.1 Registro de Atendimento ao Público',
                                        hiddenName: 'pa_record_type',
                                        width: 250,
                                        choiceId: 'inspection.RECORD_TYPE',
                                        value: 1
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 72,
                                columnWidth: 0.3,
                                items: [
                                    {
                                        fieldLabel: 'Aplicativo(s)',
                                        xtype: 'textfield',
                                        name: 'pa_apps',
                                        width: 245,

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 100,
                                columnWidth: 0.25,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Data de abertura',
                                        width: 150,
                                        name: 'pa_opening_date',
                                    },
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
                                labelWidth: 170,
                                columnWidth: 0.33,
                                items: [
                                    {
                                        fieldLabel: '2.2 Possui Termo de Abertura',
                                        xtype: 'combo',
                                        hiddenName: 'pa_has_openind_term',
                                        width: 180,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 105,
                                columnWidth: 0.33,
                                items: [
                                    {
                                        fieldLabel: 'Possui Numeração',
                                        xtype: 'combo',
                                        hiddenName: 'pa_has_numeration',
                                        width: 245,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 140,
                                columnWidth: 0.33,
                                items: [
                                    {
                                        fieldLabel: 'Possui Folhas Rubricadas',
                                        xtype: 'combo',
                                        hiddenName: 'pa_has_signed_sheets',
                                        width: 210,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 80,
                        items: [
                            {
                                fieldLabel: '2.3 Em ordem',
                                xtype: 'combo',
                                hiddenName: 'pa_ordered',
                                width: 270,
                                value: 1,
                                editable: false,
                                triggerAction: 'all',
                                store: [
                                    [1, ''],
                                    [2, 'SIM'],
                                    [3, 'NÃO'],
                                ],
                            }
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 190,
                        items: [
                            {
                                fieldLabel: '2.4 Observações/Determinações',
                                xtype: 'textarea',
                                name: 'pa_observation',
                                width: 920,
                                height: 125,
                            }
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
                                text: 'Atendimentos registrados mensalmente',
                                style: {fontWeight: 'bold',},
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            this.getRegistrationPublicAttendanceGrid(cfg),
                        ]
                    },
                ]
            });
        }
        return this._publicAttendanceForm;
    },

    getBookOfRegisterOutCourtLawSuitControlGrid: function(cfg) {
        if(!this._outCourtLawSuitGrid) {
            this._outCourtLawSuitGrid = Ext._create('corregedoria.inspection.inspection.filling.regularityofservices.bookofregisteroutcourtlawsuitcontrol.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 135,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
            });
            this.getBookOfRegisterOutCourtLawSuitControlGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._outCourtLawSuitGrid;
    },

    getOutCourtLawSuitControlForm: function(cfg) {
        if(!this._outCourtLawSuitControlForm) {
            this._outCourtLawSuitControlForm = Ext._create('Ext.form.FieldSet', {
                title: '3. Controle de Procedimentos Extrajudiciais',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
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
                                labelWidth: 75,
                                columnWidth: 0.45,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: '3.1 Controle',
                                        hiddenName: 'oclsc_record_type',
                                        width: 395,
                                        choiceId: 'inspection.RECORD_TYPE',
                                        value: 1,
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 72,
                                columnWidth: 0.3,
                                items: [
                                    {
                                        fieldLabel: 'Aplicativo(s)',
                                        xtype: 'textfield',
                                        name: 'oclsc_apps',
                                        width: 245,

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 100,
                                columnWidth: 0.25,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Data de abertura',
                                        width: 150,
                                        name: 'oclsc_opening_date',
                                    },
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
                                labelWidth: 170,
                                columnWidth: 0.33,
                                items: [
                                    {
                                        fieldLabel: '3.2 Possui Termo de Abertura',
                                        xtype: 'combo',
                                        hiddenName: 'oclsc_has_openind_term',
                                        width: 180,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 105,
                                columnWidth: 0.33,
                                items: [
                                    {
                                        fieldLabel: 'Possui Numeração',
                                        xtype: 'combo',
                                        hiddenName: 'oclsc_has_numeration',
                                        width: 245,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 140,
                                columnWidth: 0.33,
                                items: [
                                    {
                                        fieldLabel: 'Possui Folhas Rubricadas',
                                        xtype: 'combo',
                                        hiddenName: 'oclsc_has_signed_sheets',
                                        width: 210,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 80,
                        items: [
                            {
                                fieldLabel: '3.3 Em ordem',
                                xtype: 'combo',
                                hiddenName: 'oclsc_ordered',
                                width: 270,
                                value: 1,
                                editable: false,
                                triggerAction: 'all',
                                store: [
                                    [1, ''],
                                    [2, 'SIM'],
                                    [3, 'NÃO'],
                                ],
                            }
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 190,
                        items: [
                            {
                                fieldLabel: '3.4 Observações/Determinações',
                                xtype: 'textarea',
                                name: 'oclsc_observation',
                                width: 920,
                                height: 125,
                            }
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        style: {marginTop: '10px', marginBottom: '5px', fontSize: '13px'},
                        items: [
                            {
                                xtype: 'label',
                                text: 'Controle dos Procedimentos Extrajudiciais existentes na Promotoria de Justiça inspecionada',
                                style: 'fontWeight: bold;',
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        style: {marginBottom: '10px', fontSize: '13px'},
                        items: [
                            {
                                xtype: 'label',
                                text: 'Registros Obrigatórios: Notícias de Fato, Procedimentos Preparatórios e Inquéritos Civis, Procedimentos Administrativos e Procedimentos Investigatórios Criminais (PICs)',
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            this.getBookOfRegisterOutCourtLawSuitControlGrid(cfg),
                        ]
                    },
                ]
            });
        }
        return this._outCourtLawSuitControlForm;
    },

    getBookOfRegisterCourtLawSuitControlGrid: function(cfg) {
        if(!this._courtLawSuitGrid) {
            this._courtLawSuitGrid = Ext._create('corregedoria.inspection.inspection.filling.regularityofservices.bookofregistercourtlawsuitcontrol.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 135,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
            });
            this.getBookOfRegisterCourtLawSuitControlGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._courtLawSuitGrid;
    },

    getCourtLawSuitControlForm: function(cfg) {
        if(!this._courtLawSuitControlForm) {
            this._courtLawSuitControlForm = Ext._create('Ext.form.FieldSet', {
                title: '4. Controle de Procedimentos Judiciais',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
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
                                labelWidth: 75,
                                columnWidth: 0.45,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: '4.1 Controle',
                                        hiddenName: 'clsc_record_type',
                                        width: 395,
                                        choiceId: 'inspection.RECORD_TYPE',
                                        value: 1,
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 72,
                                columnWidth: 0.3,
                                items: [
                                    {
                                        fieldLabel: 'Aplicativo(s)',
                                        xtype: 'textfield',
                                        name: 'clsc_apps',
                                        width: 245,

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 100,
                                columnWidth: 0.25,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Data de abertura',
                                        width: 150,
                                        name: 'clsc_opening_date',
                                    },
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
                                labelWidth: 170,
                                columnWidth: 0.33,
                                items: [
                                    {
                                        fieldLabel: '4.2 Possui Termo de Abertura',
                                        xtype: 'combo',
                                        hiddenName: 'clsc_has_openind_term',
                                        width: 180,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 105,
                                columnWidth: 0.33,
                                items: [
                                    {
                                        fieldLabel: 'Possui Numeração',
                                        xtype: 'combo',
                                        hiddenName: 'clsc_has_numeration',
                                        width: 245,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 140,
                                columnWidth: 0.33,
                                items: [
                                    {
                                        fieldLabel: 'Possui Folhas Rubricadas',
                                        xtype: 'combo',
                                        hiddenName: 'clsc_has_signed_sheets',
                                        width: 210,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 80,
                        items: [
                            {
                                fieldLabel: '4.3 Em ordem',
                                xtype: 'combo',
                                hiddenName: 'clsc_ordered',
                                width: 270,
                                value: 1,
                                editable: false,
                                triggerAction: 'all',
                                store: [
                                    [1, ''],
                                    [2, 'SIM'],
                                    [3, 'NÃO'],
                                ],
                            }
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 190,
                        items: [
                            {
                                fieldLabel: '4.4 Observações/Determinações',
                                xtype: 'textarea',
                                name: 'clsc_observation',
                                width: 920,
                                height: 125,
                            }
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
                                text: 'Controle de Processos Judiciais existentes na Promotoria de Justiça inspecionada',
                                style: {fontWeight: 'bold',},
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            this.getBookOfRegisterCourtLawSuitControlGrid(cfg),
                        ]
                    },
                ]
            });
        }
        return this._courtLawSuitControlForm;
    },

    getRegistrationCourtLawsuitReceivedGrid: function(cfg) {
        if(!this._registrationCourtLawsuitReceivedGrid) {
            this._registrationCourtLawsuitReceivedGrid = Ext._create('corregedoria.inspection.inspection.filling.regularityofservices.registrationcourtlawsuitreceived.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 135,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
            });
            this.getRegistrationCourtLawsuitReceivedGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._registrationCourtLawsuitReceivedGrid;
    },

    getRegistrationCourtLawsuitReturnedGrid: function(cfg) {
        if(!this._registrationCourtLawsuitReturnedGrid) {
            this._registrationCourtLawsuitReturnedGrid = Ext._create('corregedoria.inspection.inspection.filling.regularityofservices.registrationcourtlawsuitreturned.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 135,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
            });
            this.getRegistrationCourtLawsuitReturnedGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._registrationCourtLawsuitReturnedGrid;
    },

    getCourtLawSuitCountForm: function(cfg) {
        if(!this._courtLawSuitCountForm) {
            this._courtLawSuitCountForm = Ext._create('Ext.form.FieldSet', {
                title: '5. Quantitativo de Procedimentos Judiciais',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
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
                                labelWidth: 320,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '5.1 Processos pendentes de citação/intimação - Urgentes',
                                        xtype: 'numberfield',
                                        name: 'clsct_number_of_processes_pending_citation_urgent',
                                        width: 70,

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 320,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '5.2 Processos pendentes de citação/intimação',
                                        xtype: 'numberfield',
                                        name: 'clsct_number_of_processes_pending_citation',
                                        width: 70,

                                    }
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
                                labelWidth: 320,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '5.3 Processos pendentes de ciência',
                                        xtype: 'numberfield',
                                        name: 'clsct_number_of_processes_pending_science',
                                        width: 70,

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 320,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '5.4 Processos com prazo em aberto',
                                        xtype: 'numberfield',
                                        name: 'clsct_processes_with_open_deadline',
                                        width: 70,

                                    }
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
                                labelWidth: 320,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '5.5 Decurso de prazo nos últimos 30 dias',
                                        xtype: 'numberfield',
                                        name: 'clsct_expired_deadline_the_last_30_days',
                                        width: 70,

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 320,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '5.6 Decurso de prazo há mais de 30 dias',
                                        xtype: 'numberfield',
                                        name: 'clsct_expired_deadline_more_than_30_days_ago',
                                        width: 70,

                                    }
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
                                labelWidth: 320,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '5.7 Decurso de prazo no período da inspeção/correição',
                                        xtype: 'numberfield',
                                        name: 'clsct_expired_deadline_in_the_period_of_inspection',
                                        width: 70,

                                    }
                                ]
                            },
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
                                text: '5.8 Número de processos RECEBIDOS no período da inspeção',
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            this.getRegistrationCourtLawsuitReceivedGrid(cfg),
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
                                text: '5.9 Número de processos DEVOLVIDOS no período da inspeção',
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            this.getRegistrationCourtLawsuitReturnedGrid(cfg),
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 190,
                        style: {margin: '10px', fontSize: '13px'},
                        items: [
                            {
                                fieldLabel: '5.10 Observações/Determinações',
                                xtype: 'textarea',
                                name: 'clsct_observation',
                                width: 920,
                                height: 125,
                                allowBlank: true,
                            }
                        ]
                    },
                ]
            });
        }
        return this._courtLawSuitCountForm;
    },

    getOutCourtLawSuitCountForm: function(cfg) {
        if(!this._outCourtLawSuitCountForm) {
            this._outCourtLawSuitCountForm = Ext._create('Ext.form.FieldSet', {
                title: '6. Quantitativo de Procedimentos Extrajudiciais',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
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
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '6.1 Número de Processos Extrajudiciais em andamento',
                                        xtype: 'numberfield',
                                        name: 'oclsct_number_of_procedures_in_progress',
                                        width: 70,

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '6.2 Número de Processos Extrajudiciais em atraso',
                                        xtype: 'numberfield',
                                        name: 'oclsct_number_of_procedures_in_arrears',
                                        width: 70,

                                    }
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
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '6.3 Procedimentos Extrajudiciais devidamente registrados e autuados',
                                        xtype: 'combo',
                                        hiddenName: 'oclsct_correctly_registered_procedures',
                                        width: 100,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '6.4 Número de Ações Civis Públicas e Medidas ajuizadas no último ano',
                                        xtype: 'numberfield',
                                        name: 'oclsct_number_of_public_civil_actions_in_the_last_year',
                                        width: 70,

                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 230,
                                        style: { paddingLeft: '210px' },
                                        items: [
                                            {
                                                fieldLabel: 'Destas, quantas foram de improbidade',
                                                xtype: 'numberfield',
                                                name: 'oclsct_number_of_acp_administrative_dishonesty',
                                                width: 70,

                                            }
                                        ]
                                    },
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
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '6.5 Número de Recomendações expedidas no último ano',
                                        xtype: 'numberfield',
                                        name: 'oclsct_number_of_recommendations_issued_in_the_last_year',
                                        width: 70,

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '6.6 Número de Termos de Ajustamento de Conduta celebrados no último ano',
                                        xtype: 'numberfield',
                                        name: 'oclsct_number_of_conduct_adjustment_terms_in_the_last_year',
                                        width: 70,

                                    },
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
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '6.7 Número de audiências públicas no último ano',
                                        xtype: 'numberfield',
                                        name: 'oclsct_number_of_public_audiences_in_the_last_year',
                                        width: 70,

                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '6.8 Número de Procedimentos Extrajudiciais instaurados no último ano',
                                        xtype: 'numberfield',
                                        name: 'oclsct_number_of_procedures_instituted_in_the_last_year',
                                        width: 70,

                                    },
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
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '6.9 Número de Processos Extrajudiciais arquivados no último ano',
                                        xtype: 'numberfield',
                                        name: 'oclsct_number_of_procedures_archived_in_the_last_year',
                                        width: 70,

                                    }
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 190,
                        items: [
                            {
                                fieldLabel: '6.10 Observações/Determinações',
                                xtype: 'textarea',
                                name: 'oclsct_observation',
                                width: 900,
                                height: 125,
                            }
                        ]
                    },
                ]
            });
        }
        return this._outCourtLawSuitCountForm;
    },

    getRegistrationCourtLawsuitElectoralReceivedGrid: function(cfg) {
        if(!this._registrationCourtLawsuitElectoralReceivedGrid) {
            this._registrationCourtLawsuitElectoralReceivedGrid = Ext._create('corregedoria.inspection.inspection.filling.regularityofservices.registrationcourtlawsuitelectoralreceived.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 135,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
                 disabled: (cfg.values.electoral_applicable == 2 ? false : true),
            });
            this.getRegistrationCourtLawsuitElectoralReceivedGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._registrationCourtLawsuitElectoralReceivedGrid;
    },

    getRegistrationCourtLawsuitElectoralReturnedGrid: function(cfg) {
        if(!this._registrationCourtLawsuitElectoralReturnedGrid) {
            this._registrationCourtLawsuitElectoralReturnedGrid = Ext._create('corregedoria.inspection.inspection.filling.regularityofservices.registrationcourtlawsuitelectoralreturned.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 135,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
                 disabled: (cfg.values.electoral_applicable == 2 ? false : true),
            });
            this.getRegistrationCourtLawsuitElectoralReturnedGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._registrationCourtLawsuitElectoralReturnedGrid;
    },

    getCourtLawSuitElectoralCountForm: function(cfg) {
        if(!this._courtLawSuitElectoralCountForm) {
            this._courtLawSuitElectoralCountForm = Ext._create('Ext.form.FieldSet', {
                title: '7. Quantitativo de Processos Judiciais Eleitorais',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
                items:[
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        style: {margin: '10px', fontSize: '13px'},
                        items: [
                            {
                                xtype: 'label',
                                text: '7.1 Número de processos eleitorais RECEBIDOS no período da inspeção',
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            this.getRegistrationCourtLawsuitElectoralReceivedGrid(cfg),
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
                                text: '7.2 Número de processos eleitorais DEVOLVIDOS no período da inspeção',
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            this.getRegistrationCourtLawsuitElectoralReturnedGrid(cfg),
                        ]
                    },
                ]
            });
        }
        return this._courtLawSuitElectoralCountForm;
    },

    getOutCourtLawSuitElectoralCountForm: function(cfg) {
        if(!this._outCourtLawSuitElectoralCountForm) {
            this._outCourtLawSuitElectoralCountForm = Ext._create('Ext.form.FieldSet', {
                title: '8. Quantitativo de Procedimentos Extrajudiciais Eleitorais',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
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
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '8.1 Número de Processos Extrajudiciais em andamento',
                                        xtype: 'numberfield',
                                        name: 'oclsect_number_of_procedures_in_progress',
                                        width: 70,
                                        disabled: (cfg.values.electoral_applicable == 2 ? false : true),

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '8.2 Número de Processos Extrajudiciais em atraso',
                                        xtype: 'numberfield',
                                        name: 'oclsect_number_of_procedures_in_arrears',
                                        width: 70,
                                        disabled: (cfg.values.electoral_applicable == 2 ? false : true),

                                    }
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
                                labelWidth: 440,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        fieldLabel: '8.3 Procedimentos Extrajudiciais devidamente registrados e autuados',
                                        xtype: 'combo',
                                        hiddenName: 'oclsect_correctly_registered_procedures',
                                        width: 100,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                        disabled: (cfg.values.electoral_applicable == 2 ? false : true),
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 190,
                        items: [
                            {
                                fieldLabel: '8.4 Observações/Determinações',
                                xtype: 'textarea',
                                name: 'oclsect_observation',
                                width: 900,
                                height: 125,
                                disabled: (cfg.values.electoral_applicable == 2 ? false : true),
                            }
                        ]
                    },
                ]
            });
        }
        return this._outCourtLawSuitElectoralCountForm;
    },

    getProcessesForAnalysisPerformanceInAudiencesGrid: function(cfg) {
        if(!this._processesForAnalysisPerformanceInAudiences) {
            this._processesForAnalysisPerformanceInAudiences = Ext._create('corregedoria.inspection.inspection.filling.regularityofservices.processesforanalysisperformanceinaudiences.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 150,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
            });
            this.getProcessesForAnalysisPerformanceInAudiencesGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._processesForAnalysisPerformanceInAudiences;
    },

    getAnalysisPerformanceInAudiencesForm: function(cfg) {
        if(!this._analysisPerformanceInAudiencesForm) {
            this._analysisPerformanceInAudiencesForm = Ext._create('Ext.form.FieldSet', {
                title: '9. Análise da Atuação nas Audiências',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
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
                                labelWidth: 310,
                                columnWidth: 0.45,
                                items: [
                                    {
                                        fieldLabel: '9.1 Constam processos analisados na Inspeção anterior',
                                        xtype: 'combo',
                                        hiddenName: 'apia_processes_analyzed_in_the_previous_inspection',
                                        width: 120,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, 'NÃO SE APLICA'],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 425,
                                columnWidth: 0.55,
                                items: [
                                    {
                                        fieldLabel: '9.2 Nessa Inspeção foi realizada vistoria em feitos escolhidos aleatoriamente',
                                        xtype: 'combo',
                                        hiddenName: 'apia_survey_in_randomly_chosen_processes',
                                        width: 120,
                                        value: 1,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, 'NÃO SE APLICA'],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    }
                                ]
                            },
                        ]
                    },
                    this.getProcessesForAnalysisPerformanceInAudiencesGrid(cfg),
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 95,
                        style: {margin: '10px', fontSize: '13px'},
                        items: [
                            {
                                fieldLabel: '7.3 Observações',
                                xtype: 'textarea',
                                name: 'apia_observation',
                                width: 995,
                                height: 75,
                            }
                        ]
                    },
                ]
            });
        }
        return this._analysisPerformanceInAudiencesForm;
    },

    getEditor: function (cfg) {
        if (!this._ckeditoField) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, {
                allowBlank: true,
                startupFocus: false,
                editorConfig: {
                    forcePasteAsPlainText: true
                },
            });
            this._ckeditoField = Ext._create('toolkit.fields.CKEditor', cfg);
        }
        return this._ckeditoField;
    },

    getAnalysisPerformanceInJuryTribunalSessionForm: function(cfg) {
        if(!this._analysisPerformanceInJuryTribunalSessionForm) {
            this._analysisPerformanceInJuryTribunalSessionForm = Ext._create('Ext.form.FieldSet', {
                title: '10. Análise da Atuação em Sessão Plenária do Tribunal do Júri',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
                    this.getEditor({
                        name: 'apijts_analysis',
                        width: 1100,
                        height: 500
                    })
                ]
            });
        }
        return this._analysisPerformanceInJuryTribunalSessionForm;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'DA REGULARIDADE DOS SERVIÇOS',
            layout: 'form',
            frame: true,
            height: 575,
            border: false,
            autoScroll: true,
            overflow: 'auto',
            bodyStyle: 'padding: 5px',
            items: [
                this.getExecutionOrganManagementForm(cfg),
                this.getPublicAttendanceForm(cfg),
                this.getOutCourtLawSuitControlForm(cfg),
                this.getCourtLawSuitControlForm(cfg),
                this.getCourtLawSuitCountForm(cfg),
                this.getOutCourtLawSuitCountForm(cfg),
                this.getCourtLawSuitElectoralCountForm(cfg),
                this.getOutCourtLawSuitElectoralCountForm(cfg),
                this.getAnalysisPerformanceInAudiencesForm(cfg),
                this.getAnalysisPerformanceInJuryTribunalSessionForm(cfg),
            ],
        });

        Ext.apply(cfg, {

        });

        corregedoria.inspection.inspection.filling.regularityofservices.Launcher.superclass.constructor.call(this, cfg);

    }
});
