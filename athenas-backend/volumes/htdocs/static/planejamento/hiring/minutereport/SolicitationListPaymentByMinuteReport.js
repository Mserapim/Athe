Ext._define('planning.hiring.minutereport.SolicitationListPaymentByMinuteReport', {
    extend: 'planning.hiring.minutereport.BaseReportWindow',

    title: 'Listagem de Pagamentos por Ata',

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
                        name: "minute_number",
                        xtype: "rest-autocompletefield",
                        rest: "planning.hiring.minute.MinuteRestful"
                    },
                    {
                        fieldLabel: 'Status',
                        hiddenName: 'status',
                        name: 'status',
                        xtype: 'combo',
                        store: [
                            [1, 'Ativa'],
                            [2, 'Concluída'],
                            [3, 'Cancelada'],
                            [4, 'Revogada'],
                            [5, 'Suspensa'],
                            [6, 'Finalizada'],
                        ],
                        triggerAction: 'all',
                        width: 185
                    },
                    {
                        allowBlank: true,
                        fieldLabel: "Contratado",
                        name: "provider",
                        xtype: "rest-autocompletefield",
                        rest: "rh.pessoa.Restful"
                    },
                    {
                        allowBlank: true,
                        fieldLabel: "Solicitação",
                        name: "solicitation",
                        xtype: "rest-autocompletefield",
                        rest: "planning.hiring.minutesolicitation.MinuteSolicitationRestful"
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
                                        name: 'data_inicial',
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
                                        name: 'data_final',
                                        xtype: 'datefield',
                                    }
                            }
                        ]
                    },
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

        engine.mq.Report.request({
                report: '/to/mpe/planejamento/solicitation_list_payment_by_minute',
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'listagem_pagamentos_por_ata' + new Date().format("d/m/Y"),
                        report_name: 'Listagem de Pagamentos por Ata',
                    }
                ),
            });
        if(!preventClose) this.close();
    },
});
