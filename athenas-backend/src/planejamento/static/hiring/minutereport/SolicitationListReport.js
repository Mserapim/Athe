Ext._define('planning.hiring.minutereport.SolicitationListReport', {
    extend: 'planning.hiring.minutereport.BaseReportWindow',

    title: 'Listagem de Pedidosx',

    _getDocumentsFields: function (cfg) {
        return [
            {
                title: 'Pedido',
                xtype: 'fieldset',
                collapsible: true,
                labelAlign: 'top',
                items: [
                    {
                        allowBlank: true,
                        fieldLabel: "Número da Pedido",
                        name: "solicitation_id",
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
                        hiddenName: 'solicitation_status',
                        xtype: 'combo',
                        store: [
                            [1, 'Em Edição'],
                            [2, 'Solicitado'],
                            [3, 'Aprovado'],
                            [4, 'Recusado'],
                            [5, 'Cancelado'],
                            [6, 'Contratado'],
                        ],
                        triggerAction: 'all',
                        width: 185
                    },
                ]
            },
            {
                title: 'Ata',
                xtype: 'fieldset',
                collapsible: true,
                labelAlign: 'top',
                items: [
                    {
                        allowBlank: true,
                        fieldLabel: "Número da Ata",
                        name: "minute_id",
                        xtype: "rest-autocompletefield",
                        rest: "planning.hiring.minute.MinuteRestful"
                    },
                    {
                        allowBlank: true,
                        fieldLabel: "Contratado",
                        name: "provider_id",
                        xtype: "rest-autocompletefield",
                        rest: "rh.pessoa.Restful"
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
                            { property: 'tipo__in', value: ['M', 'S'], stage: 1002 }
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

    generate: function (type) {
        var values = this.getFormPanel().getForm().getValues();

        if (values.expiration_from) {
            inicio_parts = values.expiration_from.split('/');
            values.expiration_from = inicio_parts[2] + '-' + inicio_parts[1] + '-' + inicio_parts[0];
        }

        if (values.expiration_until) {
            fim_parts = values.expiration_until.split('/');
            values.expiration_until = fim_parts[2] + '-' + fim_parts[1] + '-' + fim_parts[0];
        }

        if (isNaN(values.employee_id) || values.employee_id < 0)
            values.employee_id = 0;

        if (values.minutesupervisor_kind === "")
            values.minutesupervisor_kind = 1;

        if (values.minutesupervisor_status === "")
            values.minutesupervisor_status = 1;

        engine.mq.Report.request({
            report: '/to/mpe/planejamento/solicitation_list',
            el: this.getEl(),
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                values,
                {
                    outfile: 'listagem_pedidos_' + new Date().format("d/m/Y"),
                    report_name: 'Listagem de Pedidos',
                }
            ),
        }, type);
    },

    getButtons: function (cfg) {
        if (!this._buttons) {
            var me = this;
            this._buttons = [];
            this._buttons.push({
                xtype: 'splitbutton',
                text: 'Gerar Requisição',
                iconCls: 'icon-ged icon-ged-application-pdf',
                handler: function () {
                    me.generate(cfg);
                },
                menu: {
                    items: [
                        {
                            text: 'Arquivo PDF ',
                            type: 'PDF',
                            iconCls: 'icon-ged icon-ged-application-pdf',
                            scope: this,
                            handler: function (item) {
                                this.generate(item.type);
                            }
                        },
                        {
                            text: 'Arquivo ODT',
                            type: 'ODT',
                            iconCls: 'icon-ged icon-ged-application-msword',
                            scope: this,
                            handler: function (item) {
                                this.generate(item.type);
                            }
                        },
                        {
                            text: 'Arquivo XLS',
                            type: 'XLS',
                            iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                            scope: this,
                            handler: function (item) {
                                this.generate(item.type);
                            }
                        },
                    ]
                },
            });
            this._buttons.push(
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            );
        }

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                modal: true,
                resizable: false,
                border: false
            }
        );

        Ext.apply(
            cfg,
            {
                items: [
                    this.getFormPanel(),
                ],
                buttons: [
                    this.getButtons()
                ]
            }
        );
        planning.hiring.minutereport.BaseReportWindow.superclass.constructor.call(this, cfg);
    }
});
