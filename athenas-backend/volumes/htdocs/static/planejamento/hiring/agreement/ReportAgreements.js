Ext._define('planning.hiring.agreement.ReportAgreements', {
    extend: 'planning.hiring.agreement.ReportWindowBase',

    title: 'Listagem de Contratações',

    _getDocumentsFields: function(cfg) {
        return [
            {
                title: 'Contrato',
                xtype: 'fieldset',
                collapsible: true,
                labelAlign: 'top',
                items: [
                    {
                        allowBlank: true,
                        fieldLabel: "Contratado",
                        name: "provider",
                        xtype: "rest-autocompletefield",
                        rest: "rh.pessoa.Restful"
                    },
                    {
                        allowBlank: true,
                        fieldLabel: "Número",
                        name: "agreement",
                        xtype: "rest-autocompletefield",
                        rest: "planning.hiring.agreement.Restful"
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items:
                                    {
                                        columnWidth: '0.5',
                                        layout: 'form',
                                        items: {
                                            xtype: "checkboxchoicefield",
                                            singleSelection: false,
                                            labelWidth: 35,
                                            checkconfig: {
                                                xtype: 'radiogroup',
                                                name: "agreement_kind",
                                                fieldLabel: 'Tipo',
                                                choiceId: "contrato.TIPO_CONTRATO",
                                                columns: 1,
                                            },
                                        }
                                    },
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items:
                                    {
                                        fieldLabel: 'Status',
                                        hiddenName: 'agreement_status',
                                        xtype: 'combo',
                                        store: [
                                            [1, 'TODOS'],
                                            [2, 'SOMENTE ATIVOS'],
                                            [3, 'SOMENTE INATIVOS'],
                                        ],
                                        triggerAction: 'all',
                                        width: 185
                                    }
                            }
                        ]
                    },
                    {
                        layout: 'column',
                        labelAlign: 'top',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items:
                                    {
                                        width: 188,
                                        allowBlank: false,
                                        fieldLabel: 'Início',
                                        name: 'expiration_from',
                                        xtype: 'datefield',
                                    }
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items:
                                    {
                                        width: 188,
                                        allowBlank: false,
                                        fieldLabel: 'Fim',
                                        name: 'expiration_until',
                                        xtype: 'datefield',
                                    }
                            }
                        ]
                    }
                ]
            },
            {
                title: 'Fiscal',
                xtype: 'fieldset',
                collapsible: true,
                labelAlign: 'top',
                items: [
                    {
                        allowBlank: true,
                        fieldLabel: "Nome",
                        name: "employee_id",
                        xtype: "rest-autocompletefield",
                        rest: "rh.employee.Restful",
                        preFilter: [
                            {property: 'tipo__in', value: ['M', 'S'], stage: 1002}
                        ],
                        width: 385
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items:
                                    {
                                        fieldLabel: 'Tipo',
                                        hiddenName: 'agreementsupervisor_kind',
                                        xtype: 'combo',
                                        store: [
                                            [3, 'TODOS'],
                                            [1, 'SOMENTE TITULARES'],
                                            [2, 'SOMENTE SUBSTITUTOS'],
                                        ],
                                        triggerAction: 'all',
                                        width: 188
                                    }
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items:
                                    {
                                        fieldLabel: 'Status',
                                        hiddenName: 'agreementsupervisor_status',
                                        xtype: 'combo',
                                        store: [
                                            [1, 'TODOS'],
                                            [2, 'SOMENTE ATIVOS'],
                                            [3, 'SOMENTE INATIVOS'],
                                        ],
                                        triggerAction: 'all',
                                        width: 188
                                    }
                            }
                        ]
                    }
                ]
            },
            {
                fieldLabel: 'Com Pendências',
                hiddenName: 'pending_publication',
                xtype: 'combo',
                store: [
                    ['s', 'SIM'],
                    ['n', 'NÃO'],
                ],
                triggerAction: 'all',
                width: 290
            },
        ];
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();


        if(isNaN(values.employee_id) || values.employee_id < 0)
            values.employee_id = 0;

        agreement_kind = ''
        values_keys = Object.keys(values);
        for(var i = 0; i < values_keys.length; i+=1)
            if(values_keys[i].indexOf('agreement_kind') == 0) {
                agreement_kind = agreement_kind.concat(values_keys[i][14]);
                agreement_kind = agreement_kind.concat(', ');
            }
        if(agreement_kind.length == 0)
            agreement_kind = 1
        else
            agreement_kind = agreement_kind.substring(0, agreement_kind.length-2);
        values.agreement_kind = agreement_kind;

        if (values.agreementsupervisor_kind === "") values.agreementsupervisor_kind = 1;
        if (values.agreementsupervisor_status === "") values.agreementsupervisor_status = 1;

        values.agreement = values.agreement;
        values.agreement_status = values.agreement_status;

        if(values.expiration_from) {
            inicio_parts = values.expiration_from.split('/');
            values.expiration_from = inicio_parts[2]+'-'+inicio_parts[1]+'-'+inicio_parts[0];
        }

        if(values.expiration_until) {
            fim_parts = values.expiration_until.split('/');
            values.expiration_until = fim_parts[2]+'-'+fim_parts[1]+'-'+fim_parts[0];
        }

        values.provider = values.provider;
        values.pending_publication = values.pending_publication;

        engine.mq.Report.request({
                report: '/to/mpe/planejamento/listagem_de_contratacoes',
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'listagem_contratacoes_' + new Date().format("d/m/Y"),
                        report_name: 'Listagem de Contratações',
                    }
                ),
            });
        if(!preventClose) this.close();
    },
});
