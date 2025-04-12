Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationPaymentGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.minutesolicitation.MinuteSolicitationPaymentWindow',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'pay', 'unpay', '-', 'text', 'report', '-', 'search'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Responsavel', dataIndex: 'user_display', width: 180},
                    {header: 'Valor (R$)', dataIndex: 'value', width: 70, 'renderer': toolkit.util.formatCurrency},
                    {header: 'NF', dataIndex: 'invoice', width: 90},
                    {header: 'OB', dataIndex: 'bank_order', width: 90},
                    {header: 'NE', dataIndex: 'commitmentnote_unicode', width: 90},
                    {header: 'Período de Referência', dataIndex: 'period_display', width: 160},
                    {header: 'Data do Pagamento', dataIndex: 'payment_date', width: 70, renderer: Ext.util.Format.dateRenderer('d/m/Y'), id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    getTextAction: function() {
        var rest = Ext._create('planning.hiring.minutesolicitation.MinuteSolicitationPaymentRestful');
        if(!this._paymentSolicitation)
        this._paymentSolicitation = Ext._create('Ext.Button', {
            text: 'Solicitação de Pagamento',
            iconCls: 'icon-core icon-core-reports',
            scope: this,
            handler: function() {
                
                solicitations = this.getSelectionModel().getSelections().map(
                    function (record) {
                        return record.get('pk')
                    }
                ).join();

                var mask = new Ext.LoadMask(this.getEl(), {
                    msg: 'Gerando solicitação de pagamento...'
                });

                console.log(solicitations);

                if (solicitations.length == 0)
                {
                        Ext.Msg.show({
                            title: 'Erro',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Selecione pelo menos um pagamento.'
                        });
                }
                else if(solicitations.length > 0)
                {
                    rest.paymentSolicitation(
                        // selection[0].id,
                        solicitations,
                        {
                            scope: this,
                            fn: function(message) {
                                var _window = Ext._create(
                                    'planning.hiring.meterage.DispatchTextWindow'
                                );
                                _window.setMessage(message.message);
                                _window.show();
                            }
                        },
                        {
                            fn: function(message) {
                                Ext.Msg.show({
                                    title: 'Falha na comunicação',
                                    msg: message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            fn: function() {
                                mask.hide();
                                delete mask;
                            }
                        }
                    );
                }
            }
        });

        return this._paymentSolicitation;
    },

    getPayAction: function() {
        if(!this._payAction)
            this._payAction = Ext._create('Ext.Button', {
                text: 'Lançar Pagamento',
                iconCls: 'icon-agree icon-agree-payment-finish',
                scope: this,
                handler: this._pay
            });

        return this._payAction;
    },

    _pay: function() {
        var sels = this.getSelectionModel().getSelections();

        if (sels.length > 0) {
            this._payWindow = Ext._create('planning.hiring.minutesolicitationpayment.MinuteSolicitationPaymentExecutionWindow', {
                params: {
                    payment: this.payment,
                    paymentGrid: this
                },
                callback: {
                    success: {
                        scope: this,
                        fn: function(args) {
                            this.getStore().reload();
                        }
                    }
                },
                action: 'create',
            });

            this._payWindow.show();
        }
        else {
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um registro para pagar'
            });
        }

    },

    getUnpayAction: function() {
        if(!this._unpayAction)
            this._unpayAction = Ext._create('Ext.Button', {
                text: 'Desfazer Pagamento',
                iconCls: 'icon-agree icon-agree-delete',
                scope: this,
                handler: this._unpay
            });

        return this._unpayAction;
    },

    _unpay: function() {
        var sels = this.getSelectionModel().getSelections();

        if(sels.length > 0) {
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Desfazendo Pagamento...'});

            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: 'Tem certeza que deseja desfazer o pagamento selecionado?',
                scope: this,
                fn: function(bnt) {
                    if(bnt == 'no') return;

                    mask.show();
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('PHMMinuteSolicitationPayment', 'unpay'),
                        scope: this,
                        params: {
                            pk: this.getSelectionModel().getSelected().get('pk')
                        },
                        success: function(response, opts) {
                            var obj = Ext.decode(response.responseText);

                            if (obj.success)
                                this.getStore().reload();

                            Ext.Msg.show({
                                title: this.title,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK,
                                msg: obj.message
                            });
                        },
                        failure: function(response, opts) {
                            var obj = Ext.decode(response.responseText);

                            Ext.Msg.show({
                                title: this.title,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: obj.message
                            });
                        },
                        callback: function() {
                            mask.hide();
                            mask = null;
                        }
                    });
                }
            });
        }
        else
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione os pagamentos que deseja desfazer.'
            });
    },

    getReportAction: function() {
        if(!this._reportAction)
            this._reportAction = Ext._create('Ext.Button', {
                text: 'Despacho de Pagamento da Ata',
                iconCls: 'icon-agree icon-agree-application-pdf',
                scope: this,
                handler: this._dispatch
            });

        return this._reportAction;
    },

    _dispatch: function() {
        var sels = this.getSelectionModel().getSelections();

        if (sels.length > 0) {
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action('PHMMinuteSolicitationPayment', 'get_logged_employee_id'),
                scope: this,
                params: {
                    minute: this.params.minute
                },
                success: function(response, opts) {
                    var obj = Ext.decode(response.responseText);
                    this.logged_employee_id = obj.logged_employee_id;
                    engine.mq.Report.request({
                        report: '/to/mpe/planejamento/minute_solicitation_payment_dispatch',
                        el: this.getEl(),
                        waitMessage: 'Gerando relatório...',
                        params: {
                            outfile: 'despacho_pagamento_' + new Date().format("d/m/Y"),
                            report_name: 'Despacho de Pagamento da Ata',
                            minute: this.params.minute,
                            employee_id: this.logged_employee_id,
                            payment: this.getSelectionModel().getSelections().map(
                                function(record) {
                                    return record.get('pk');
                                }
                            ).join()
                        }
                    });
                },
                failure: function(response, opts) {
                    var obj = Ext.decode(response.responseText);

                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: obj.message
                    });
                },
            });
        } else {
            Ext.Msg.show({
                title: 'Despacho',
                icon: Ext.Msg.WARNING,
                buttons: Ext.Msg.OK,
                msg: 'Selecione um pagamento para gerar o despacho'
            });
        }
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
            viewConfig: {
                scope: this,
                getRowClass: function(record) {
                    if(record.get('payment_date') != null) {
                        return 'x-grid3-green';
                    }
                    if(record.get('payment_date') == 3) {
                        return 'x-grid3-red-simple';
                    }
                }
            }
        });

        planning.hiring.minutesolicitation.MinuteSolicitationPaymentGrid.superclass.constructor.call(this, cfg);
    },
});

core.RestfulGrid.register(
    'planning.hiring.minutesolicitation.MinuteSolicitationPaymentRestful',
    'planning.hiring.minutesolicitation.MinuteSolicitationPaymentGrid'
);

