Ext._define('planning.hiring.minutereport.MinuteListBySupervisorReport', {
    extend: 'planning.hiring.minutereport.BaseReportWindow',

    title: 'Listagem de Atas por Fiscal',

    _getDocumentsFields: function(cfg) {
        return [
            {
                title: 'Ata',
                xtype: 'fieldset',
                collapsible: true,
                labelAlign: 'top',
                items: [
                    {
                        allowBlank: true,
                        fieldLabel: "Número",
                        name: "minute",
                        xtype: "rest-autocompletefield",
                        rest: "planning.hiring.minute.MinuteRestful"
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
                    },
                    {
                        fieldLabel: 'Status',
                        hiddenName: 'minute_status',
                        xtype: 'combo',
                        store: [
                            [1, 'TODOS'],
                            [2, 'SOMENTE ATIVOS'],
                            [3, 'SOMENTE INATIVOS'],
                        ],
                        triggerAction: 'all',
                        width: 185
                    },
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
                                        hiddenName: 'minutesupervisor_kind',
                                        xtype: 'combo',
                                        store: [
                                            [1, 'TODOS'],
                                            [2, 'SOMENTE TITULARES'],
                                            [3, 'SOMENTE SUBSTITUTOS'],
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
                                        hiddenName: 'minutesupervisor_status',
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
        ];
    },

    generate: function(preventClose) {
        var values = this.getFormPanel().getForm().getValues();
    
        if(values.expiration_from) {
            inicio_parts = values.expiration_from.split('/');
            values.expiration_from = inicio_parts[2]+'-'+inicio_parts[1]+'-'+inicio_parts[0];
        }

        if(values.expiration_until) {
            fim_parts = values.expiration_until.split('/');
            values.expiration_until = fim_parts[2]+'-'+fim_parts[1]+'-'+fim_parts[0];
        }
        
        if(isNaN(values.employee_id) || values.employee_id < 0)
            values.employee_id = 0;
        
        if (values.minute_status === "")
            values.minute_status = 1;

        if (values.minutesupervisor_kind === "")
            values.minutesupervisor_kind = 1;

        if (values.minutesupervisor_status === "")
            values.minutesupervisor_status = 1;

        engine.mq.Report.request({
                report: '/to/mpe/planejamento/minute_list_by_supervisor',
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'listagem_atas_por_fiscal' + new Date().format("d/m/Y"),
                        report_name: 'Listagem de Atas por Fiscal',
                    }
                ),
            });
        if(!preventClose) this.close();
    },
});
